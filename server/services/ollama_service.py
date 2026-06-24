# ============================================================================
# Ollama 大模型调用服务
# 负责调用 qwen2.5:7b 进行对话生成
# 负责调用 qwen3-embedding:4b 生成文本向量
# ============================================================================
import ollama
from typing import List, Optional


class OllamaService:
    """
    Ollama 服务类
    封装了对 Ollama API 的调用，提供大模型对话和文本嵌入功能
    """

    def __init__(self, base_url: str = 'http://localhost:11434',
                 llm_model: str = 'qwen2.5:7b',
                 embedding_model: str = 'qwen3-embedding:4b'):
        """
        初始化 Ollama 服务
        :param base_url: Ollama 服务地址
        :param llm_model: 大语言模型名称
        :param embedding_model: 嵌入模型名称
        """
        self.client = ollama.Client(host=base_url)
        self.llm_model = llm_model
        self.embedding_model = embedding_model

    def chat(self, messages: list, stream: bool = False) -> dict:
        """
        与大模型进行对话（同步）
        :param messages: 消息列表，格式：[{"role": "user", "content": "你好"}]
        :param stream: 是否流式输出
        :return: 模型响应
        """
        return self.client.chat(model=self.llm_model, messages=messages, stream=stream)

    def chat_stream(self, messages: list):
        """
        流式对话，返回生成器，逐 token 产出
        :param messages: 消息列表
        :yield: 每个 token 的响应块
        """
        stream = self.client.chat(model=self.llm_model, messages=messages, stream=True)
        for chunk in stream:
            yield chunk

    def embed_text(self, text: str) -> List[float]:
        """
        将文本转换为向量嵌入
        :param text: 待转换的文本
        :return: 浮点数向量列表
        """
        response = self.client.embeddings(model=self.embedding_model, prompt=text)
        return response['embedding']

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量将文档文本转换为向量嵌入
        :param texts: 待转换的文本列表
        :return: 浮点数向量列表的列表
        """
        return [self.embed_text(text) for text in texts]

    def check_connection(self) -> bool:
        """
        检查 Ollama 服务是否可用
        :return: True=可用，False=不可用
        """
        try:
            self.client.list()
            return True
        except Exception:
            return False
