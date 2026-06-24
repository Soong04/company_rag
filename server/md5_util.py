# ============================================================================
# 密码加密工具类
# v2.0 — 从 MD5 迁移至 SHA-256 加盐，兼容旧密码
# ============================================================================
import hashlib
import os


# 加盐使用的固定盐值（生产环境建议从环境变量读取）
SALT = os.environ.get('PASSWORD_SALT', 'enterprise-qa-salt-2024')


def md5_encrypt(text: str) -> str:
    """
    [已弃用] 对字符串进行 MD5 加密
    保留用于兼容旧密码验证
    """
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()


def hash_password(password: str) -> str:
    """
    对密码进行 SHA-256 加盐哈希
    格式: sha256$salt$hash
    """
    salt = SALT
    h = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f'sha256${salt}${h}'


def verify_password(input_password: str, stored_hash: str) -> bool:
    """
    验证密码是否匹配（同时支持旧版 MD5 和新版 SHA-256）

    新版格式: sha256$salt$hash
    旧版格式: 32位md5-hex
    """
    if not stored_hash or not input_password:
        return False

    # 新版 SHA-256 加盐验证
    if stored_hash.startswith('sha256$'):
        parts = stored_hash.split('$')
        if len(parts) == 3:
            _, salt, expected = parts
            h = hashlib.sha256((input_password + salt).encode('utf-8')).hexdigest()
            return h == expected

    # 旧版 MD5 兼容验证
    return md5_encrypt(input_password) == stored_hash


def is_legacy_md5(stored_hash: str) -> bool:
    """检查是否为旧版 MD5 密码（需要升级）"""
    return bool(stored_hash) and not stored_hash.startswith('sha256$')


DEFAULT_PASSWORD_MD5 = 'e10adc3949ba59abbe56e057f20f883e'
