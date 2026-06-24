# ============================================================================
# RAG（检索增强生成）服务
# 核心业务：用户提问 → 混合检索 → 重排序 → 构建上下文 → LLM 回答
# ============================================================================
from typing import List, Dict, Any, Optional
from services.vector_service import VectorService
from services.hybrid_retriever import HybridRetriever
from services.reranker_service import RerankerService


class RAGService:
    """
    RAG 服务类
    检索增强生成核心流程：混合检索 → RRF 融合 → 重排序 → LLM 生成
    """

    def __init__(self, llm_service, vector_service: VectorService,
                 persist_dir: str = None):
        self.llm = llm_service
        self.vector = vector_service
        self.hybrid = HybridRetriever(
            persist_dir=persist_dir or './chroma_data'
        )
        self.reranker = RerankerService()
        self.reranker_enabled = self.reranker.is_available()

    def enable_reranker(self, enabled: bool = True):
        """启用或禁用重排序"""
        self.reranker_enabled = enabled
        if enabled:
            self.reranker_enabled = self.reranker.is_available()
        return self.reranker_enabled

    def _retrieve(self, question: str, top_k: int = 5) -> tuple:
        """
        混合检索流程：向量检索 → BM25 → RRF 融合 → 可选重排序
        返回 (context_str, sources_list)
        """
        # 1. 向量检索
        question_embedding = self.llm.embed_text(question)
        vector_results = self.vector.search(question_embedding, top_k * 2)

        # 2. 混合检索（BM25 + 向量，RRF 融合）
        fused = self.hybrid.hybrid_search(question, vector_results, top_k=top_k * 2)

        # 3. 重排序
        if self.reranker_enabled and fused:
            fused = self.reranker.rerank(question, fused, top_k=top_k)

        # 4. 构建上下文
        context_parts = []
        sources = []
        for idx, item in enumerate(fused[:top_k]):
            text = item.get('text', '')
            meta = item.get('metadata', {})
            context_parts.append(f"[来源{idx+1}] {text}")
            sources.append({
                'title': meta.get('title', '未知来源'),
                'doc_id': meta.get('doc_id', ''),
                'relevance_score': round(
                    item.get('rerank_score', item.get('rrf_score', 0)), 4
                ),
            })

        context = '\n\n'.join(context_parts) if context_parts else ''
        return context, sources

    def _build_messages(self, question: str, context: str) -> list:
        """构建对话消息列表"""
        if context:
            system_prompt = """你是一个专业的企业知识库问答助手。请严格基于以下提供的知识内容回答用户的问题。

## 回答要求
1. 只使用提供的知识内容回答问题，不要编造信息
2. 如果知识不足，明确告知"知识库中没有相关信息"
3. 引用来源时标注 [来源X]，如"根据公司制度 [来源1]"
4. 使用中文回答，语言简洁专业
5. 分点列出，优先使用结构化格式（编号列表）

## 回答结构
- 先直接回答核心问题
- 再补充相关细节
- 最后给出引用来源

===== 知识内容 START =====
{context}
===== 知识内容 END =====

请基于以上知识内容回答："""
        else:
            system_prompt = """你是一个专业的企业知识库问答助手。

## 注意事项
- 知识库中未找到与问题相关的内容，请如实告知用户
- 可以基于你的通用知识提供参考信息，但需明确标注「以下为通用参考信息，非知识库内容」
- 使用中文回答，保持简洁专业"""

        return [
            {"role": "system", "content": system_prompt.format(context=context) if context else system_prompt},
            {"role": "user", "content": question}
        ]

    def ask(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """同步问答：检索 → 生成 → 返回完整结果"""
        context, sources = self._retrieve(question, top_k)
        messages = self._build_messages(question, context)
        response = self.llm.chat(messages)

        return {
            'answer': response['message']['content'],
            'sources': sources,
            'model': self.llm.llm_model
        }

    def ask_stream(self, question: str, top_k: int = 5):
        """
        流式问答：先检索，再逐 token 流式生成
        yield 格式: {"type": "sources", "data": [...]}
                    {"type": "token", "data": "部分回答"}
                    {"type": "done", "data": {"conversation_id": ...}}
        """
        context, sources = self._retrieve(question, top_k)
        messages = self._build_messages(question, context)

        yield {'type': 'sources', 'data': sources}

        full_answer = ''
        for chunk in self.llm.chat_stream(messages):
            content = chunk.get('message', {}).get('content', '')
            if content:
                full_answer += content
                yield {'type': 'token', 'data': content}

        yield {'type': 'done', 'data': {'answer': full_answer, 'sources': sources}}
