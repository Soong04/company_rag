# ============================================================================
# Chroma 向量数据库服务
# 负责知识文档的向量存储与相似度检索
# ============================================================================
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import uuid


class VectorService:
    """
    Chroma 向量数据库服务类
    提供文档向量的增删改查功能
    """

    def __init__(self, persist_dir: str = './chroma_data',
                 collection_name: str = 'enterprise_knowledge'):
        """
        初始化 Chroma 客户端
        :param persist_dir: 持久化存储目录
        :param collection_name: 集合名称
        """
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection_name = collection_name
        # 获取或创建集合（使用余弦距离）
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}      # 使用余弦相似度
        )

    def add_documents(self, texts: List[str], metadata: List[Dict],
                      embeddings: List[List[float]]) -> List[str]:
        """
        添加文档到向量数据库
        :param texts: 文档文本列表
        :param metadata: 元数据列表（含文档ID、标题等信息）
        :param embeddings: 向量嵌入列表
        :return: 生成的文档ID列表
        """
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        self.collection.add(
            documents=texts,
            metadatas=metadata,
            embeddings=embeddings,
            ids=ids
        )
        return ids

    def search(self, query_embedding: List[float], top_k: int = 5) -> Dict[str, Any]:
        """
        根据查询向量进行相似度检索
        :param query_embedding: 查询文本的向量
        :param top_k: 返回最相似的结果数量
        :return: 检索结果（含文档内容和元数据）
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results

    def delete_by_metadata(self, field: str, value: Any) -> None:
        """
        根据元数据字段删除文档
        :param field: 元数据字段名（如 doc_id）
        :param value: 字段值
        """
        self.collection.delete(where={field: value})

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        获取集合统计信息
        :return: 统计信息字典
        """
        count = self.collection.count()
        return {"total_documents": count}
