# ============================================================================
# 认证路由（登录/登出/注册）
# ============================================================================
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from md5_util import md5_encrypt, verify_password

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    POST /api/auth/login
    Body: {"username": "xxx", "password": "xxx"}
    """
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求数据为空'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401

    if not verify_password(password, user.password):
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401

    if user.status != 1:
        return jsonify({'code': 403, 'message': '该账号已被禁用，请联系管理员'}), 403

    # 如果是旧版 MD5 密码，自动升级为 SHA-256 加盐
    from md5_util import is_legacy_md5, hash_password
    if is_legacy_md5(user.password):
        user.password = hash_password(password)
        db.session.flush()

    # 登录成功
    login_user(user, remember=True)

    # 更新最后登录信息
    user.last_login_ip = request.remote_addr
    user.last_login_time = db.func.current_timestamp()
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'user': user.to_dict()
        }
    })


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    logout_user()
    return jsonify({'code': 200, 'message': '已退出登录'})


@auth_bp.route('/current_user', methods=['GET'])
@login_required
def get_current_user():
    """获取当前登录用户信息"""
    return jsonify({
        'code': 200,
        'data': {
            'user': current_user.to_dict()
        }
    })
