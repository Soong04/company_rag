#!/bin/bash
# ============================================================================
# Docker 入口脚本：等待 MySQL 就绪 → 初始化数据库 → 启动应用
# ============================================================================
set -e

# 1. 等待 MySQL 就绪
if [ -n "$DB_HOST" ]; then
    echo "[entrypoint] 等待 MySQL $DB_HOST:$DB_PORT ..."
    until mysqladmin ping -h "$DB_HOST" -P "$DB_PORT" \
        -u "$DB_USER" -p"$DB_PASS" --silent 2>/dev/null; do
        echo "  MySQL 未就绪，等待 2 秒 ..."
        sleep 2
    done
    echo "[entrypoint] MySQL 就绪"
fi

# 2. 初始化/迁移数据库（幂等）
echo "[entrypoint] 初始化数据库 ..."
python init_db.py || echo "[entrypoint] 数据库初始化（可忽略已有数据警告）"

# 3. 启动应用
echo "[entrypoint] 启动服务 ..."
exec "$@"
