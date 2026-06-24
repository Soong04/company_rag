# ============================================================================
# 系统日志模型
# ============================================================================
from . import db


class SysLog(db.Model):
    """系统日志模型"""
    __tablename__ = 'tb_sys_log'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True,
                   comment='日志ID，主键自增')
    user_id = db.Column(db.Integer, db.ForeignKey('tb_user.id'), nullable=False,
                        comment='操作用户ID')
    action = db.Column(db.String(64), nullable=False,
                       comment='操作类型（login/query/upload/delete等）')
    detail = db.Column(db.String(500), default=None,
                       comment='操作详情')
    ip_address = db.Column(db.String(64), default=None,
                           comment='操作IP')
    create_time = db.Column(db.DateTime, nullable=False,
                            default=db.func.current_timestamp(),
                            comment='创建时间')

    def __repr__(self):
        return f'<SysLog {self.action}>'
