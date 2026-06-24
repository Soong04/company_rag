# ============================================================================
# 用户模型（User）
# 对应 tb_user 表
# ============================================================================
from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'tb_user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   comment='用户ID，主键自增')
    username = db.Column(db.String(64), nullable=False, unique=True,
                         comment='用户名，唯一')
    password = db.Column(db.String(255), nullable=False,
                         comment='密码（MD5加密存储）')
    real_name = db.Column(db.String(64), default=None,
                          comment='真实姓名')
    email = db.Column(db.String(128), default=None,
                      comment='邮箱地址')
    phone = db.Column(db.String(20), default=None,
                      comment='手机号码')
    role = db.Column(db.Enum('admin', 'user'), nullable=False, default='user',
                     comment='角色：admin=管理员，user=普通用户')
    status = db.Column(db.Integer, nullable=False, default=1,
                       comment='状态：1=启用，0=禁用')
    avatar_url = db.Column(db.String(255), default=None,
                           comment='头像URL')
    last_login_ip = db.Column(db.String(64), default=None,
                              comment='最后登录IP')
    last_login_time = db.Column(db.DateTime, default=None,
                                comment='最后登录时间')
    create_time = db.Column(db.DateTime, nullable=False,
                            default=db.func.current_timestamp(),
                            comment='创建时间')
    update_time = db.Column(db.DateTime, nullable=False,
                            default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp(),
                            comment='更新时间')

    # 关系
    documents = db.relationship('Document', backref='uploader', lazy='dynamic',
                                foreign_keys='Document.upload_user_id')
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def is_admin(self) -> bool:
        """判断是否为管理员"""
        return self.role == 'admin'

    def is_active_user(self) -> bool:
        """判断用户是否启用"""
        return self.status == 1

    def to_dict(self) -> dict:
        """转换为字典（不包含密码）"""
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'status': self.status,
            'avatar_url': self.avatar_url,
            'last_login_ip': self.last_login_ip,
            'last_login_time': self.last_login_time.strftime('%Y-%m-%d %H:%M:%S')
                               if self.last_login_time else None,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S')
                           if self.create_time else None,
        }
