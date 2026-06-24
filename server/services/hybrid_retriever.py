# ============================================================================
# 混合检索服务（BM25 + 向量检索）
# ============================================================================
import os
import pickle
import re
import jieba
import numpy as np
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any


# 每个 BM25 子索引的最大文档数（避免全量重建）
# 达到上限后新建子索引，搜索时合并结果
_MAX_DOCS_PER_INDEX = 200


class HybridRetriever:
    """
    混合检索器：结合 BM25 关键词检索 + Chroma 向量检索
    使用 RRF（Reciprocal Rank Fusion）融合排序

    BM25 使用多子索引策略：每个子索引上限 _MAX_DOCS_PER_INDEX 篇文档，
    新增文档只影响当前子索引，避免每次添加都重建全量索引。
    """

    def __init__(self, persist_dir: str = './chroma_data'):
        self.persist_dir = persist_dir
        self.bm25_index_path = os.path.join(persist_dir, 'bm25_index.pkl')
        # bm25_indices: list of dicts, each {"bm25": BM25Okapi, "docs": [...], "metadatas": [...]}
        self.bm25_indices = []
        self._load_bm25_indices()

    # -------- BM25 索引管理 --------

    def _tokenize(self, text: str) -> List[str]:
        """中文分词"""
        if not text:
            return []
        return list(jieba.cut(text))

    def _load_bm25_indices(self):
        """从磁盘加载 BM25 多子索引"""
        if os.path.exists(self.bm25_index_path):
            try:
                with open(self.bm25_index_path, 'rb') as f:
                    data = pickle.load(f)
                    indices_data = data.get('indices', [])
                    self.bm25_indices = []
                    for idx in indices_data:
                        docs = idx.get('docs', [])
                        metadatas = idx.get('metadatas', [])
                        if docs:
                            tokenized = [self._tokenize(d) for d in docs]
                            self.bm25_indices.append({
                                'bm25': BM25Okapi(tokenized),
                                'docs': docs,
                                'metadatas': metadatas,
                            })
            except Exception as e:
                print(f'[HybridRetriever] 加载 BM25 索引失败: {e}')
                self.bm25_indices = []

    def _save_bm25_indices(self):
        """保存 BM25 多子索引到磁盘"""
        os.makedirs(self.persist_dir, exist_ok=True)
        indices_data = [
            {'docs': idx['docs'], 'metadatas': idx['metadatas']}
            for idx in self.bm25_indices
        ]
        with open(self.bm25_index_path, 'wb') as f:
            pickle.dump({'indices': indices_data}, f)

    def _reset(self):
        """重置所有 BM25 索引"""
        self.bm25_indices = []

    def add_documents(self, texts: List[str], metadatas: List[Dict]):
        """
        添加文档到 BM25 索引（只影响当前子索引，不会全量重建）
        如果当前子索引已满则自动新建子索引
        """
        if not texts:
            return

        tokenized = [self._tokenize(t) for t in texts]

        # 找到或创建当前活跃子索引
        if (not self.bm25_indices or
                len(self.bm25_indices[-1]['docs']) >= _MAX_DOCS_PER_INDEX):
            # 新建子索引
            self.bm25_indices.append({
                'bm25': BM25Okapi(tokenized),
                'docs': list(texts),
                'metadatas': list(metadatas),
            })
        else:
            # 追加到当前子索引并局部重建
            current = self.bm25_indices[-1]
            current['docs'].extend(texts)
            current['metadatas'].extend(metadatas)
            all_tokenized = [self._tokenize(d) for d in current['docs']]
            current['bm25'] = BM25Okapi(all_tokenized)

        self._save_bm25_indices()

    def delete_by_metadata(self, field: str, value: Any):
        """根据元数据从所有子索引中删除文档"""
        for idx in list(self.bm25_indices):
            remaining_docs = []
            remaining_metas = []
            for i, meta in enumerate(idx['metadatas']):
                if str(meta.get(field, '')) != str(value):
                    remaining_docs.append(idx['docs'][i])
                    remaining_metas.append(meta)

            if len(remaining_docs) != len(idx['docs']):
                # 当前子索引有文档被删除，局部重建
                if remaining_docs:
                    tokenized = [self._tokenize(d) for d in remaining_docs]
                    idx['bm25'] = BM25Okapi(tokenized)
                    idx['docs'] = remaining_docs
                    idx['metadatas'] = remaining_metas
                else:
                    # 子索引完全清空，移除
                    self.bm25_indices.remove(idx)

        self._save_bm25_indices()

    def rebuild_from_chunks(self, chunks: List[str], metadatas: List[Dict]):
        """
        从 chunk 列表重建整个 BM25 索引（全量重建）
        按 _MAX_DOCS_PER_INDEX 自动分片
        """
        self._reset()
        if not chunks:
            self._save_bm25_indices()
            return

        # 按 _MAX_DOCS_PER_INDEX 分片构建子索引
        for i in range(0, len(chunks), _MAX_DOCS_PER_INDEX):
            batch_docs = chunks[i:i + _MAX_DOCS_PER_INDEX]
            batch_metas = metadatas[i:i + _MAX_DOCS_PER_INDEX]
            tokenized = [self._tokenize(d) for d in batch_docs]
            self.bm25_indices.append({
                'bm25': BM25Okapi(tokenized),
                'docs': list(batch_docs),
                'metadatas': list(batch_metas),
            })

        self._save_bm25_indices()

    # -------- BM25 检索 --------

    def bm25_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        BM25 关键词检索（合并所有子索引结果）
        各子索引得分不可直接比较，所以统一取 top_k 后按原始得分二次排序
        """
        if not self.bm25_indices:
            return []

        tokenized_query = self._tokenize(query)
        per_index_top = max(top_k, 50)  # 每个子索引取更多候选，确保合并后不丢失

        collected = []
        for idx in self.bm25_indices:
            scores = idx['bm25'].get_scores(tokenized_query)
            top_indices = np.argsort(scores)[::-1][:per_index_top]

            for doc_idx in top_indices:
                if scores[doc_idx] > 0:
                    collected.append({
                        'text': idx['docs'][doc_idx],
                        'metadata': idx['metadatas'][doc_idx],
                        'score': float(scores[doc_idx]),
                    })

        # 按得分降序排列，取 top_k
        collected.sort(key=lambda x: x['score'], reverse=True)
        for rank, item in enumerate(collected[:top_k]):
            item['rank'] = rank

        return collected[:top_k]

    # -------- RRF 融合 --------

    @staticmethod
    def rrf_fusion(results_list: List[List[Dict]], k: int = 60, top_k: int = 10) -> List[Dict]:
        """
        Reciprocal Rank Fusion 融合多路检索结果
        :param results_list: 多路检索结果列表
        :param k: RRF 常数（通常 60）
        :param top_k: 返回结果数
        """
        score_map = {}
        for results in results_list:
            for rank, item in enumerate(results):
                text_key = item.get('text', '')
                if not text_key:
                    continue
                if text_key not in score_map:
                    score_map[text_key] = {
                        'text': text_key,
                        'metadata': item.get('metadata', {}),
                        'sources': [],
                    }
                score_map[text_key]['rrf_score'] = score_map[text_key].get('rrf_score', 0) + 1.0 / (k + rank + 1)
                score_map[text_key]['sources'].append(item)

        # 按 RRF 分数排序
        sorted_items = sorted(score_map.values(), key=lambda x: x['rrf_score'], reverse=True)
        return sorted_items[:top_k]

    # -------- 混合检索 --------

    def hybrid_search(self, query: str, vector_results: List[Dict] = None, top_k: int = 10) -> List[Dict]:
        """
        混合检索（BM25 + 向量结果融合）
        :param query: 查询文本
        :param vector_results: 已从 Chroma 获取的向量检索结果
        :param top_k: 最终返回结果数
        """
        # BM25 检索
        bm25_results = self.bm25_search(query, top_k=top_k * 2)

        # 将向量结果转为统一格式
        unified_vector = []
        if vector_results:
            for i, doc_text in enumerate(vector_results.get('documents', [[]])[0]):
                meta = vector_results.get('metadatas', [[]])[0][i] if vector_results.get('metadatas') else {}
                distance = vector_results.get('distances', [[]])[0][i] if vector_results.get('distances') else 0
                unified_vector.append({
                    'text': doc_text,
                    'metadata': meta,
                    'score': 1 - float(distance),  # 距离转相似度
                    'rank': i,
                })

        # RRF 融合
        results_list = []
        if bm25_results:
            results_list.append(bm25_results)
        if unified_vector:
            results_list.append(unified_vector)

        if not results_list:
            return []

        return self.rrf_fusion(results_list, top_k=top_k)
