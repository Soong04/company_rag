# ============================================================================
# Flask 后端 Dockerfile
# ============================================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- 运行阶段 ----------
FROM python:3.11-slim

WORKDIR /app

# 仅复制运行时需要的系统库
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    default-mysql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 复制 site-packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/chroma_data /app/uploads /app/data/documents

EXPOSE 5000

# 启动入口：等待 MySQL 就绪 → 初始化数据库 → 启动 gunicorn
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:create_app()"]
