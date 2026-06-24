# ============================================================================
# 问答反馈模型
# ============================================================================
from . import db


class Feedback(db.Model):
    """问答反馈模型"""
    __tablename__ = 'tb_feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   comment='反馈ID')
    message_id = db.Column(db.Integer, db.ForeignKey('tb_message.id'), nullable=False,
                            comment='关联消息ID')
    user_id = db.Column(db.Integer, db.ForeignKey('tb_user.id'), nullable=False,
                        comment='反馈用户ID')
    rating = db.Column(db.Integer, nullable=False,
                       comment='评分：1=赞，-1=踩')
    comment = db.Column(db.String(500), default=None,
                        comment='反馈备注')
    create_time = db.Column(db.DateTime, nullable=False,
                            default=db.func.current_timestamp(),
                            comment='创建时间')

    def __repr__(self):
        return f'<Feedback {self.id} rating={self.rating}>'

    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'rating': self.rating,
            'comment': self.comment,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
