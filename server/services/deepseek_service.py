# ============================================================================
# DeepSeek API 大模型调用服务
# 替换 Ollama，改为调用 DeepSeek 在线 API
# 支持对话生成（同步 + 流式）和文本嵌入
# ============================================================================
import logging
from typing import List
from openai import OpenAI

logger = logging.getLogger(__name__)


class DeepSeekService:
    """
    DeepSeek API 服务类
    封装对 DeepSeek API（OpenAI 兼容接口）的调用
    提供大模型对话和文本嵌入功能
    """

    def __init__(self,
                 api_key: str,
                 base_url: str = 'https://api.deepseek.com',
                 llm_model: str = 'deepseek-chat',
                 embedding_model: str = 'deepseek-embedding',
                 timeout: int = 120):
        """
        初始化 DeepSeek 服务
        :param api_key: DeepSeek API 密钥
        :param base_url: API 地址（默认 https://api.deepseek.com）
        :param llm_model: 对话模型名称（默认 deepseek-chat）
        :param embedding_model: 嵌入模型名称（默认 deepseek-embedding）
        :param timeout: 请求超时时间（秒）
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout
        )
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.base_url = base_url

    # -------- 对话（同步） --------

    def chat(self, messages: list, stream: bool = False) -> dict:
        """
        与大模型进行对话（同步）
        :param messages: 消息列表，格式：[{"role": "user", "content": "你好"}]
        :param stream: 兼容参数，同步模式下忽略
        :return: 兼容上层调用的响应格式
        """
        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=messages,
            stream=False,
        )
        return {
            'message': {
                'content': response.choices[0].message.content or ''
            }
        }

    # -------- 对话（流式） --------

    def chat_stream(self, messages: list):
        """
        流式对话，逐 token 产出
        :param messages: 消息列表
        :yield: 兼容上层调用的每个 token 响应块
        """
        stream = self.client.chat.completions.create(
            model=self.llm_model,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield {'message': {'content': delta.content}}

    # -------- 文本嵌入 --------

    def embed_text(self, text: str) -> List[float]:
        """
        将文本转换为向量嵌入
        :param text: 待转换的文本
        :return: 浮点数向量列表
        """
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量将文档文本转换为向量嵌入（一次 API 调用，比逐条快 N 倍）
        :param texts: 待转换的文本列表
        :return: 浮点数向量列表的列表
        """
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=texts
        )
        # 按 index 排序确保返回顺序与输入一致
        sorted_data = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_data]

    # -------- 服务检查 --------

    def check_connection(self) -> bool:
        """
        检查 DeepSeek API 是否可用
        :return: True=可用，False=不可用
        """
        try:
            self.client.embeddings.create(
                model=self.embedding_model,
                input='connection-test'
            )
            return True
        except Exception as e:
            logger.warning(f'DeepSeek API 连接失败: {e}')
            return False
