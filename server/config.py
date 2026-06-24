# ============================================================================
# Flask 应用配置文件
# ============================================================================
import os
from datetime import timedelta


class Config:
    """应用基础配置"""

    # Flask 密钥（用于 Session 加密）
    SECRET_KEY = os.environ.get('SECRET_KEY', 'enterprise-qa-secret-key-2024')

    # Session 有效期 24 小时
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # -------- MySQL 数据库配置 --------
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', 3306)            # 指定端口 3306
    DB_NAME = os.environ.get('DB_NAME', 'db_enterprise_qa')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASS = os.environ.get('DB_PASS', '123456')

    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        '?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # -------- DeepSeek API 配置（替代 Ollama） --------
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
    DEEPSEEK_BASE_URL = os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    DEEPSEEK_LLM_MODEL = os.environ.get('DEEPSEEK_LLM_MODEL', 'deepseek-chat')
    DEEPSEEK_EMBEDDING_MODEL = os.environ.get('DEEPSEEK_EMBEDDING_MODEL', 'deepseek-embedding')

    # -------- Ollama 配置（已弃用，改用 DeepSeek API） --------
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    LLM_MODEL = 'qwen2.5:7b'                  # 大语言模型
    EMBEDDING_MODEL = 'qwen3-embedding:4b'    # 文本嵌入模型

    # -------- Chroma 配置 --------
    CHROMA_PERSIST_DIR = os.environ.get('CHROMA_PERSIST_DIR', './chroma_data')
    CHROMA_COLLECTION_NAME = 'enterprise_knowledge'

    # -------- 文件上传配置 --------
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', './uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024      # 最大上传 50MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt', 'md'}

    # -------- 分块参数 --------
    CHUNK_SIZE = 500                            # 文本分块大小（字符数）
    CHUNK_OVERLAP = 50                          # 分块重叠大小
    RETRIEVAL_TOP_K = 5                         # 检索返回的最相关块数
