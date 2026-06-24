-- ============================================================================
-- 升级脚本 001：为 tb_document 表添加 content 列
-- 适用场景：已有数据库（通过 schema.sql 创建的老表缺少 content 列）
-- 使用方法: mysql -h localhost -P 3306 -u root -p db_enterprise_qa < sql/migrate_001_add_content.sql
-- ============================================================================

USE db_enterprise_qa;

-- 检查 content 列是否已存在，不存在则添加
SET @dbname = 'db_enterprise_qa';
SET @tablename = 'tb_document';
SET @columnname = 'content';

SET @stmt = NULL;
SELECT IF(
    COUNT(*) = 0,
    'ALTER TABLE tb_document ADD COLUMN content TEXT DEFAULT NULL COMMENT ''文档完整内容（全文搜索用）'' AFTER content_summary',
    'SELECT 1 AS already_exists'
) INTO @stmt
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = @dbname
  AND TABLE_NAME = @tablename
  AND COLUMN_NAME = @columnname;

PREPARE stmt FROM @stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
