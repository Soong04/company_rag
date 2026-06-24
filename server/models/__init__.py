# ============================================================================
# 数据模型包初始化
# ============================================================================
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .knowledge import Category, Document
from .conversation import Conversation, Message
from .log import SysLog
from .feedback import Feedback
