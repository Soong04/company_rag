# 企业知识库问答系统（Enterprise QA RAG System）

基于 RAG（检索增强生成）架构的企业知识库问答系统，支持管理员和普通用户双角色，集成 Ollama 大模型与 Chroma 向量数据库。

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    客户端 (client/)                    │
│            Vue3 + Element Plus + ECharts             │
├─────────────────────────────────────────────────────┤
│                     HTTP / REST API                   │
├─────────────────────────────────────────────────────┤
│                 服务端 (server/)                       │
│        Flask + Flask-SQLAlchemy + Flask-Login        │
│           ChromaDB Client + Ollama SDK               │
├──────────────────┬──────────────────────────────────┤
│    MySQL 8 (3306)  │       Chroma 向量数据库           │
│  db_enterprise_qa  │   qwen3-embedding:4b 嵌入模型    │
├──────────────────┴──────────────────────────────────┤
│               Ollama (本地部署)                       │
│            qwen2.5:7b（LLM 推理）                      │
│         qwen3-embedding:4b（文本嵌入）                  │
└─────────────────────────────────────────────────────┘
```

## 技术栈

### 后端
- **Web 框架**: Flask 3.1 + Flask-SQLAlchemy
- **数据库**: MySQL 8（端口 3306）
- **向量数据库**: Chroma（持久化模式）
- **大模型**: Ollama（qwen2.5:7b + qwen3-embedding:4b）

### 前端
- **框架**: Vue 3 + Vue Router + Pinia
- **UI 组件库**: Element Plus
- **图表**: ECharts
- **HTTP 请求**: Axios

## 功能特性

- **双角色登录**：管理员后台 + 普通用户问答
- **智能问答**：基于 RAG 技术的知识库问答，引用来源可追溯
- **知识库管理**：文档上传、分类管理、全文检索
- **管理后台**：数据统计图表、用户管理、操作日志
- **多格式支持**：支持 PDF、DOCX、TXT、MD 文档格式

## 项目结构

```
├── server/                    # 后端 Flask 项目
│   ├── app.py                 # Flask 应用入口
│   ├── config.py              # 配置文件
│   ├── init_db.py             # 数据库初始化脚本
│   ├── md5_util.py            # MD5 加密工具
│   ├── requirements.txt       # Python 依赖
│   ├── models/                # 数据模型
│   ├── routes/                # 路由控制器
│   ├── services/              # 业务逻辑服务
│   │   ├── ollama_service.py  # Ollama LLM 调用
│   │   ├── vector_service.py  # Chroma 向量服务
│   │   └── rag_service.py     # RAG 核心服务
│   └── sql/                   # SQL 脚本
│
├── client/                    # 前端 Vue3 项目
│   ├── src/
│   │   ├── api/               # API 接口
│   │   ├── router/            # 路由配置
│   │   ├── store/             # 状态管理
│   │   ├── views/             # 页面组件
│   │   └── layouts/           # 布局组件
│   └── package.json
│
└── README.md
```

## 环境准备

### 前提条件

| 软件 | 版本 | 说明 |
|------|------|------|
| Python | >= 3.10 | 后端运行环境 |
| Node.js | >= 18 | 前端运行环境 |
| MySQL | 8.0+ | 关系数据库，端口 3306 |
| Ollama | 最新版 | 本地 LLM 推理引擎 |

### 安装 Ollama 模型

```bash
# 拉取大语言模型（用于对话生成）
ollama pull qwen2.5:7b

# 拉取文本嵌入模型（用于向量化）
ollama pull qwen3-embedding:4b
```

### 初始化数据库

```bash
# 方法一：使用 Python 脚本自动初始化
cd server
python init_db.py

# 方法二：手动执行 SQL 脚本
mysql -h localhost -P 3306 -u root -p < server/sql/schema.sql
mysql -h localhost -P 3306 -u root -p < server/sql/test_data.sql
```

## 启动项目

### 后端启动

```bash
cd server
pip install -r requirements.txt
python app.py
# 服务默认运行在 http://localhost:5000
```

### 前端启动

```bash
cd client
npm install
npm run dev
# 服务默认运行在 http://localhost:5173
```

## 测试账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | 123456 | 可访问管理后台 |
| 普通用户 | zhangsan | 123456 | 可使用问答功能 |
| 普通用户 | lisi | 123456 | 可使用问答功能 |
| 普通用户 | wangwu | 123456 | 可使用问答功能 |
| 禁用用户 | zhaoliu | 123456 | 账号已被禁用 |

## RAG 问答流程

```
用户提问 → 向量化（qwen3-embedding:4b）
         → Chroma 相似度检索（top-k=5）
         → 拼接知识上下文 + System Prompt
         → qwen2.5:7b 生成回答
         → 返回回答 + 引用来源
```

## 关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 密码加密 | MD5 | 按需求使用 MD5，生产环境建议加盐 |
| 向量数据库 | Chroma（持久化模式） | 轻量级，无需单独部署 |
| 文本分块 | 500字符 + 50重叠 | 兼顾上下文完整性和检索精度 |
| 相似度度量 | 余弦相似度 | 对文本向量效果好 |
| UI 组件库 | Element Plus | 成熟稳定，中文友好 |
