# ============================================================================
# 重排序服务（Cross-Encoder Reranker）
# ============================================================================
import os
from typing import List, Dict, Any


# 默认跨编码器模型（多语言，支持中文）
DEFAULT_RERANKER_MODEL = 'BAAI/bge-reranker-v2-m3'
# 备用轻量模型
FALLBACK_RERANKER_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'


class RerankerService:
    """
    重排序服务：对检索结果进行精细化排序
    使用 Cross-Encoder 模型对 (query, passage) 对进行评分
    """

    def __init__(self, model_name: str = None, device: str = 'cpu'):
        self.model_name = model_name or DEFAULT_RERANKER_MODEL
        self.device = device
        self.model = None
        self._loaded = False

    def _load_model(self):
        """延迟加载模型（首次使用时加载）"""
        if self._loaded:
            return True
        try:
            from sentence_transformers import CrossEncoder
            print(f'[Reranker] 加载模型: {self.model_name}...')
            self.model = CrossEncoder(
                self.model_name,
                device=self.device,
                max_length=512,
            )
            self._loaded = True
            print(f'[Reranker] 模型加载完成')
            return True
        except Exception as e:
            print(f'[Reranker] 加载 {self.model_name} 失败: {e}')
            # 尝试备用模型
            if self.model_name != FALLBACK_RERANKER_MODEL:
                print(f'[Reranker] 尝试备用模型: {FALLBACK_RERANKER_MODEL}')
                self.model_name = FALLBACK_RERANKER_MODEL
                return self._load_model()
            return False

    def is_available(self) -> bool:
        """检查重排序是否可用"""
        return self._load_model()

    def rerank(self, query: str, candidates: List[Dict], top_k: int = None) -> List[Dict]:
        """
        对候选文档进行重排序
        :param query: 原始查询
        :param candidates: 候选文档列表 [{'text': ..., 'metadata': ..., ...}, ...]
        :param top_k: 返回前 k 个结果（默认返回全部）
        :return: 按相关性降序排列的结果
        """
        if not candidates:
            return []

        if not self._load_model():
            # 模型不可用，原序返回
            return candidates

        top_k = top_k or len(candidates)

        # 构建 (query, passage) 对
        pairs = [[query, c.get('text', '')] for c in candidates]

        try:
            # Cross-Encoder 评分
            scores = self.model.predict(pairs, show_progress_bar=False)
            if hasattr(scores, 'tolist'):
                scores = scores.tolist()

            # 确保 scores 是列表
            if isinstance(scores, (int, float)):
                scores = [scores]

            # 将分数附加到结果
            for i, score in enumerate(scores):
                if i < len(candidates):
                    candidates[i]['rerank_score'] = float(score)

            # 按分数降序排列
            reranked = sorted(candidates, key=lambda x: x.get('rerank_score', 0), reverse=True)
            return reranked[:top_k]

        except Exception as e:
            print(f'[Reranker] 评分失败: {e}')
            return candidates[:top_k]
