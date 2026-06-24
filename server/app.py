# ============================================================================
# Flask 应用入口
# 企业知识库问答系统（Enterprise QA RAG System）
# ============================================================================
import os
import json
import logging
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate

from config import Config
from models import db, User, Conversation, Message, SysLog

# ---------- 日志配置 ----------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
# 压制过于 verbose 的第三方库日志
logging.getLogger('chromadb').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)


# ============================================================================
# 全局服务实例（在 create_app 中初始化，通过 current_app.extensions 共享）
# ============================================================================

_SERVICE_KEYS = {
    'llm': 'rag_llm_service',
    'vector': 'rag_vector_service',
    'rag': 'rag_rag_service',
}


def get_llm():
    """获取全局 LLM 服务实例（DeepSeek / Ollama）"""
    from flask import current_app
    return current_app.extensions.get(_SERVICE_KEYS['llm'])


def get_vector_service():
    """获取全局 VectorService 实例"""
    from flask import current_app
    return current_app.extensions.get(_SERVICE_KEYS['vector'])


def get_rag_service():
    """获取全局 RAGService 实例（惰性创建）"""
    from flask import current_app
    rag = current_app.extensions.get(_SERVICE_KEYS['rag'])
    if rag is None:
        from services.rag_service import RAGService
        llm_svc = get_llm()
        vector = get_vector_service()
        if llm_svc and vector:
            rag = RAGService(
                llm_svc, vector,
                persist_dir=current_app.config.get('CHROMA_PERSIST_DIR', './chroma_data')
            )
            current_app.extensions[_SERVICE_KEYS['rag']] = rag
    return rag


# ============================================================================
# Flask 应用工厂
# ============================================================================

def create_app():
    """创建 Flask 应用实例"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 初始化扩展
    db.init_app(app)
    Migrate(app, db)
    CORS(app, supports_credentials=True)

    # 初始化 Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = '/api/auth/login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ---- 初始化全局服务实例 ----
    _init_services(app)

    # 注册蓝图
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.knowledge import knowledge_bp
    from routes.chat import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(chat_bp)

    # 健康检查接口
    @app.route('/api/health')
    def health_check():
        return json.dumps({'code': 200, 'message': 'ok', 'data': {
            'service': 'Enterprise QA RAG System',
            'version': '1.0.0'
        }}), 200, {'Content-Type': 'application/json'}

    # 全局错误处理
    @app.errorhandler(404)
    def not_found(e):
        return json.dumps({'code': 404, 'message': '接口不存在'}), 404, {
            'Content-Type': 'application/json'}

    @app.errorhandler(500)
    def internal_error(e):
        return json.dumps({'code': 500, 'message': '服务器内部错误'}), 500, {
            'Content-Type': 'application/json'}

    return app


def _init_services(app):
    """初始化并注册全局服务实例"""
    try:
        from services.deepseek_service import DeepSeekService
        from services.vector_service import VectorService

        deepseek = DeepSeekService(
            api_key=app.config['DEEPSEEK_API_KEY'],
            base_url=app.config['DEEPSEEK_BASE_URL'],
            llm_model=app.config['DEEPSEEK_LLM_MODEL'],
            embedding_model=app.config['DEEPSEEK_EMBEDDING_MODEL'],
        )
        vector = VectorService(
            persist_dir=app.config['CHROMA_PERSIST_DIR'],
            collection_name=app.config['CHROMA_COLLECTION_NAME']
        )

        app.extensions[_SERVICE_KEYS['llm']] = deepseek
        app.extensions[_SERVICE_KEYS['vector']] = vector

        if deepseek.check_connection():
            logger = logging.getLogger(__name__)
            logger.info(f'DeepSeek API 连接成功 ({app.config["DEEPSEEK_BASE_URL"]})')
            logger.info(f'LLM 模型: {app.config["DEEPSEEK_LLM_MODEL"]}')
            logger.info(f'嵌入模型: {app.config["DEEPSEEK_EMBEDDING_MODEL"]}')
            logger.info(f'Chroma 向量库: {app.config["CHROMA_COLLECTION_NAME"]}')
        else:
            logger.warning(f'DeepSeek API 连接失败，请检查 API Key: {app.config["DEEPSEEK_BASE_URL"]}')
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f'服务初始化失败: {e}')
        # 不阻断启动——路由中会优雅降级


# ============================================================================
# 启动入口
# ============================================================================

if __name__ == '__main__':
    app = create_app()
    print(f'[*] 服务启动: http://0.0.0.0:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
