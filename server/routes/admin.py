# ============================================================================
# 管理员后台路由
# ============================================================================
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db
from models.user import User
from models.knowledge import Category, Document

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'code': 403, 'message': '权限不足，需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard', methods=['GET'])
@login_required
@admin_required
def dashboard():
    """
    管理员首页统计数据
    GET /api/admin/dashboard
    """
    user_count = User.query.count()
    doc_count = Document.query.count()
    active_user_count = User.query.filter_by(status=1).count()
    category_count = Category.query.count()

    # 统计各分类文档数
    category_stats = []
    categories = Category.query.filter_by(parent_id=0).all()
    for cat in categories:
        doc_num = Document.query.filter_by(category_id=cat.id).count()
        category_stats.append({
            'name': cat.name,
            'value': doc_num
        })

    return jsonify({
        'code': 200,
        'data': {
            'user_count': user_count,
            'active_user_count': active_user_count,
            'doc_count': doc_count,
            'category_count': category_count,
            'category_stats': category_stats
        }
    })


@admin_bp.route('/stats', methods=['GET'])
@login_required
@admin_required
def stats():
    """
    获取统计数据（活跃度/趋势）
    GET /api/admin/stats
    """
    from sqlalchemy import func, text

    # 近7天每天登录次数
    daily_logins = db.session.execute(
        text("""
            SELECT DATE(create_time) as date, COUNT(*) as count
            FROM tb_sys_log
            WHERE action = 'login'
              AND create_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(create_time)
            ORDER BY date
        """)
    ).fetchall()

    login_trend = [
        {'date': row[0].strftime('%m-%d'), 'count': row[1]}
        for row in daily_logins
    ]

    return jsonify({
        'code': 200,
        'data': {
            'login_trend': login_trend
        }
    })


@admin_bp.route('/logs', methods=['GET'])
@login_required
@admin_required
def get_logs():
    """
    获取操作日志列表
    GET /api/admin/logs?page=1&size=20
    """
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)

    # 使用原生 SQL 查询 tb_sys_log 表
    from sqlalchemy import text
    offset = (page - 1) * size

    logs = db.session.execute(
        text("""
            SELECT l.id, l.user_id, u.username, l.action, l.detail, l.ip_address, l.create_time
            FROM tb_sys_log l
            LEFT JOIN tb_user u ON l.user_id = u.id
            ORDER BY l.create_time DESC
            LIMIT :limit OFFSET :offset
        """),
        {'limit': size, 'offset': offset}
    ).fetchall()

    total = db.session.execute(text("SELECT COUNT(*) FROM tb_sys_log")).scalar()

    log_list = []
    for row in logs:
        log_list.append({
            'id': row[0],
            'user_id': row[1],
            'username': row[2],
            'action': row[3],
            'detail': row[4],
            'ip_address': row[5],
            'create_time': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else ''
        })

    return jsonify({
        'code': 200,
        'data': {
            'list': log_list,
            'total': total,
            'page': page,
            'size': size
        }
    })


@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """
    用户管理列表
    GET /api/admin/users?page=1&size=20&keyword=
    """
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    keyword = request.args.get('keyword', '').strip()

    query = User.query
    if keyword:
        query = query.filter(
            User.username.like(f'%{keyword}%') |
            User.real_name.like(f'%{keyword}%') |
            User.email.like(f'%{keyword}%')
        )

    pagination = query.order_by(User.create_time.desc()).paginate(
        page=page, per_page=size, error_out=False
    )

    users = [user.to_dict() for user in pagination.items]

    return jsonify({
        'code': 200,
        'data': {
            'list': users,
            'total': pagination.total,
            'page': page,
            'size': size
        }
    })


@admin_bp.route('/users', methods=['POST'])
@login_required
@admin_required
def create_user():
    """
    创建新用户（管理员）
    POST /api/admin/users
    """
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求数据为空'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400

    from md5_util import hash_password
    user = User(
        username=username,
        password=hash_password(password),
        real_name=data.get('real_name', ''),
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        role=data.get('role', 'user'),
        status=data.get('status', 1),
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'code': 200, 'message': '创建成功', 'data': {'user': user.to_dict()}})


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    """
    更新用户信息（管理员）
    PUT /api/admin/users/<id>
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求数据为空'}), 400

    if 'real_name' in data:
        user.real_name = data['real_name']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'role' in data:
        user.role = data['role']
    if 'status' in data:
        user.status = data['status']

    db.session.commit()

    return jsonify({'code': 200, 'message': '更新成功', 'data': {'user': user.to_dict()}})


@admin_bp.route('/users/<int:user_id>/toggle_status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """
    启用/禁用用户
    POST /api/admin/users/<id>/toggle_status
    """
    if user_id == current_user.id:
        return jsonify({'code': 400, 'message': '不能禁用自己'}), 400

    user = User.query.get_or_404(user_id)
    user.status = 0 if user.status == 1 else 1
    db.session.commit()

    status_text = '已启用' if user.status == 1 else '已禁用'
    return jsonify({'code': 200, 'message': f'用户{status_text}', 'data': {'user': user.to_dict()}})
