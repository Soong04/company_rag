# ============================================================================
# 对话/消息数据模型
# ============================================================================
from . import db
from datetime import datetime


class Conversation(db.Model):
    """对话记录模型"""
    __tablename__ = 'tb_conversation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   comment='对话ID，主键自增')
    user_id = db.Column(db.Integer, db.ForeignKey('tb_user.id'), nullable=False,
                        comment='用户ID，关联 tb_user.id')
    title = db.Column(db.String(255), default=None,
                      comment='对话标题（自动生成）')
    model_name = db.Column(db.String(64), default='qwen2.5:7b',
                           comment='使用的模型名称')
    message_count = db.Column(db.Integer, nullable=False, default=0,
                              comment='消息数量')
    create_time = db.Column(db.DateTime, nullable=False,
                            default=db.func.current_timestamp(),
                            comment='创建时间')
    update_time = db.Column(db.DateTime, nullable=False,
                            default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp(),
                            comment='更新时间')

    def __repr__(self):
        return f'<Conversation {self.title}>'

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'model_name': self.model_name,
            'message_count': self.message_count,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S'),
        }


class Message(db.Model):
    """消息模型"""
    __tablename__ = 'tb_message'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   comment='消息ID，主键自增')
    conversation_id = db.Column(db.Integer, db.ForeignKey('tb_conversation.id'), nullable=False,
                                comment='所属对话ID，关联 tb_conversation.id')
    role = db.Column(db.Enum('user', 'assistant', 'system'), nullable=False,
                     comment='消息角色：user=用户，assistant=AI助手，system=系统')
    content = db.Column(db.Text, nullable=False,
                        comment='消息内容')
    source_docs = db.Column(db.JSON, default=None,
                            comment='引用的知识库文档来源（JSON数组）')
    tokens_used = db.Column(db.Integer, default=0,
                            comment='消耗的Token数')
    create_time = db.Column(db.DateTime, nullable=False,
                            default=db.func.current_timestamp(),
                            comment='创建时间')

    def __repr__(self):
        return f'<Message {self.role}:{self.content[:20]}>'
