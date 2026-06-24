-- ============================================================================
-- 数据库初始化脚本
-- 目标数据库：db_enterprise_qa
-- 端口：3306
-- 字符集：utf8mb4
-- ============================================================================

-- 创建数据库（如不存在）
CREATE DATABASE IF NOT EXISTS db_enterprise_qa
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE db_enterprise_qa;

-- ============================================================================
-- 1. 用户表（tb_user）
--    存储管理员和普通用户信息
-- ============================================================================
CREATE TABLE IF NOT EXISTS tb_user (
    id              INT             AUTO_INCREMENT  COMMENT '用户ID，主键自增',
    username        VARCHAR(64)     NOT NULL        COMMENT '用户名，唯一',
    password        VARCHAR(255)    NOT NULL        COMMENT '密码（MD5加密存储）',
    real_name       VARCHAR(64)     DEFAULT NULL    COMMENT '真实姓名',
    email           VARCHAR(128)    DEFAULT NULL    COMMENT '邮箱地址',
    phone           VARCHAR(20)     DEFAULT NULL    COMMENT '手机号码',
    role            ENUM('admin', 'user') NOT NULL DEFAULT 'user'
                                                    COMMENT '角色：admin=管理员，user=普通用户',
    status          TINYINT(1)      NOT NULL DEFAULT 1
                                                    COMMENT '状态：1=启用，0=禁用',
    avatar_url      VARCHAR(255)    DEFAULT NULL    COMMENT '头像URL',
    last_login_ip   VARCHAR(64)     DEFAULT NULL    COMMENT '最后登录IP',
    last_login_time DATETIME        DEFAULT NULL    COMMENT '最后登录时间',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                    COMMENT '创建时间',
    update_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                                                    COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    INDEX idx_role (role),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='用户表——存储管理员和普通用户信息';

-- ============================================================================
-- 2. 知识库分类表（tb_category）
-- ============================================================================
CREATE TABLE IF NOT EXISTS tb_category (
    id              INT             AUTO_INCREMENT  COMMENT '分类ID，主键自增',
    name            VARCHAR(128)    NOT NULL        COMMENT '分类名称',
    parent_id       INT             DEFAULT 0       COMMENT '父分类ID，0表示顶级分类',
    sort_order      INT             NOT NULL DEFAULT 0
                                                    COMMENT '排序顺序',
    description     VARCHAR(500)    DEFAULT NULL    COMMENT '分类描述',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                    COMMENT '创建时间',
    update_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                                                    COMMENT '更新时间',
    PRIMARY KEY (id),
    INDEX idx_parent_id (parent_id),
    INDEX idx_sort_order (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='知识库分类表——用于对知识文档进行分类管理';

-- ============================================================================
-- 3. 文档表（tb_document）
--    存储上传的知识文档元信息，文本内容存储在 Chroma 向量数据库
-- ============================================================================
CREATE TABLE IF NOT EXISTS tb_document (
    id              INT             AUTO_INCREMENT  COMMENT '文档ID，主键自增',
    category_id     INT             NOT NULL        COMMENT '所属分类ID，关联 tb_category.id',
    title           VARCHAR(255)    NOT NULL        COMMENT '文档标题',
    file_type       VARCHAR(20)     DEFAULT NULL    COMMENT '文件类型（pdf/docx/txt等）',
    file_path       VARCHAR(500)    DEFAULT NULL    COMMENT '文件存储路径',
    file_size       BIGINT          DEFAULT 0       COMMENT '文件大小（字节）',
    page_count      INT             DEFAULT 0       COMMENT '文档页数/文本块数',
    content_summary VARCHAR(500)    DEFAULT NULL    COMMENT '内容摘要',
    content         MEDIUMTEXT      DEFAULT NULL    COMMENT '文档完整内容（全文搜索用）',
    status          TINYINT(1)      DEFAULT 0       NOT NULL
                                                    COMMENT '处理状态：0=待处理，1=处理中，2=已完成，-1=失败',
    chunk_count     INT             DEFAULT 0       COMMENT '文本块数量（Chroma中的分块数）',
    upload_user_id  INT             NOT NULL        COMMENT '上传用户ID，关联 tb_user.id',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                    COMMENT '创建时间',
    update_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                                                    COMMENT '更新时间',
    PRIMARY KEY (id),
    INDEX idx_category_id (category_id),
    INDEX idx_status (status),
    INDEX idx_upload_user (upload_user_id),
    FULLTEXT INDEX ft_content (content) WITH PARSER ngram,
    FULLTEXT INDEX ft_title (title) WITH PARSER ngram,
    CONSTRAINT fk_doc_category FOREIGN KEY (category_id) REFERENCES tb_category(id),
    CONSTRAINT fk_doc_uploader FOREIGN KEY (upload_user_id) REFERENCES tb_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='文档表——存储知识文档的元信息，文本内容存储在Chroma向量数据库';

-- ============================================================================
-- 4. 对话记录表（tb_conversation）
--    记录用户与 LLM 的问答历史
-- ============================================================================
CREATE TABLE IF NOT EXISTS tb_conversation (
    id              INT             AUTO_INCREMENT  COMMENT '对话ID，主键自增',
    user_id         INT             NOT NULL        COMMENT '用户ID，关联 tb_user.id',
    title           VARCHAR(255)    DEFAULT NULL    COMMENT '对话标题（自动生成）',
    model_name      VARCHAR(64)     DEFAULT 'qwen2.5:7b'
                                                    COMMENT '使用的模型名称',
    message_count   INT             NOT NULL DEFAULT 0
                                                    COMMENT '消息数量',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                    COMMENT '创建时间',
    update_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                                                    COMMENT '更新时间',
    PRIMARY KEY (id),
    INDEX idx_user_id (user_id),
    INDEX idx_update_time (update_time),
    CONSTRAINT fk_conv_user FOREIGN KEY (user_id) REFERENCES tb_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='对话记录表——记录用户与大模型的问答历史会话';

-- ============================================================================
-- 5. 消息表（tb_message）
--    存储每一条具体的问答消息
-- ============================================================================
CREATE TABLE IF NOT EXISTS tb_message (
    id              INT             AUTO_INCREMENT  COMMENT '消息ID，主键自增',
    conversation_id INT             NOT NULL        COMMENT '所属对话ID，关联 tb_conversation.id',
    role            ENUM('user', 'assistant', 'system') NOT NULL
                                                    COMMENT '消息角色：user=用户，assistant=AI助手，system=系统',
    content         TEXT            NOT NULL        COMMENT '消息内容',
    source_docs     JSON            DEFAULT NULL    COMMENT '引用的知识库文档来源（JSON数组）',
    tokens_used     INT             DEFAULT 0       COMMENT '消耗的Token数',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                    COMMENT '创建时间',
    PRIMARY KEY (id),
    INDEX idx_conversation_id (conversation_id),
    CONSTRAINT fk_msg_conversation FOREIGN KEY (conversation_id) REFERENCES tb_conversation(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='消息表——存储每一条具体的问答消息内容及引用来源';

-- ============================================================================
-- 6. 系统日志表（tb_sys_log）
--    记录用户操作日志，用于管理员统计
-- ============================================================================
CREATE TABLE IF NOT EXISTS tb_sys_log (
    id              BIGINT          AUTO_INCREMENT  COMMENT '日志ID，主键自增',
    user_id         INT             NOT NULL        COMMENT '操作用户ID',
    action          VARCHAR(64)     NOT NULL        COMMENT '操作类型（login/query/upload/delete等）',
    detail          VARCHAR(500)    DEFAULT NULL    COMMENT '操作详情',
    ip_address      VARCHAR(64)     DEFAULT NULL    COMMENT '操作IP',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                    COMMENT '创建时间',
    PRIMARY KEY (id),
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='系统日志表——记录用户操作行为，用于后台统计与分析';
