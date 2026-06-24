-- ============================================================================
-- 测试数据脚本
-- ============================================================================
USE db_enterprise_qa;

-- ---------------------------
-- 1. 用户测试数据（密码均为 123456）
--    格式兼容：支持 MD5(123456)=e10adc3949ba59abbe56e057f20f883e 或 SHA-256 加盐
--    登录后旧密码会自动升级为新格式
-- ---------------------------
INSERT INTO tb_user (username, password, real_name, email, phone, role, status) VALUES
('admin',    'e10adc3949ba59abbe56e057f20f883e', '系统管理员', 'admin@company.com',   '13800000001', 'admin', 1),
('zhangsan', 'e10adc3949ba59abbe56e057f20f883e', '张三',       'zhangsan@company.com', '13800000002', 'user',  1),
('lisi',     'e10adc3949ba59abbe56e057f20f883e', '李四',       'lisi@company.com',     '13800000003', 'user',  1),
('wangwu',   'e10adc3949ba59abbe56e057f20f883e', '王五',       'wangwu@company.com',   '13800000004', 'user',  1),
('zhaoliu',  'e10adc3949ba59abbe56e057f20f883e', '赵六',       'zhaoliu@company.com',  '13800000005', 'user',  0);
-- 说明：赵六为禁用状态用户

-- ---------------------------
-- 2. 知识库分类测试数据
-- ---------------------------
INSERT INTO tb_category (id, name, parent_id, sort_order, description) VALUES
(1, '公司制度',      0, 1, '公司内部规章制度、员工手册等'),
(2, '技术文档',      0, 2, '技术方案、开发规范、架构设计等'),
(3, '产品手册',      0, 3, '产品使用说明、功能特性介绍等'),
(4, '人力资源',      0, 4, '招聘、培训、绩效考核等人力资源相关'),
(5, '财务知识',      0, 5, '报销流程、预算管理、财务制度等'),
(6, '考勤制度',      4, 1, '考勤管理、请假流程等相关'),
(7, '招聘指南',      4, 2, '面试流程、招聘标准等'),
(8, '后端开发',      2, 1, '后端开发规范与文档'),
(9, '前端开发',      2, 2, '前端开发规范与文档');

-- ---------------------------
-- 3. 文档测试数据
-- ---------------------------
INSERT INTO tb_document (id, category_id, title, file_type, file_path, file_size, page_count, content_summary, status, chunk_count, upload_user_id) VALUES
(1, 1, '员工考勤管理制度',     'txt',  '/data/documents/attendance.txt',  12500,  5,  '公司员工考勤、请假、加班的管理规定',       2, 10, 1),
(2, 1, '公司信息安全管理制度', 'txt',  '/data/documents/security.txt',   18000,  7,  '公司信息安全管理要求与操作规范',           2, 14, 1),
(3, 2, 'RESTful API 设计规范', 'txt',  '/data/documents/api_design.txt',  15000,  6,  'RESTful API 设计原则与命名规范',            2, 12, 2),
(4, 3, '产品使用指南 V3.0',    'txt',  '/data/documents/product_guide.txt', 22000, 9,  '产品功能介绍与操作步骤说明',               2, 18, 2),
(5, 4, '2024年度招聘计划',     'txt',  '/data/documents/recruit_plan.txt',  8000,  3,  '2024年各部门招聘计划与岗位要求',           2,  6, 1),
(6, 5, '费用报销管理规定',     'txt',  '/data/documents/expense.txt',     9500,  4,  '费用报销流程、标准与审批要求',              1,  0, 3),
(7, 6, '请假申请流程',         'txt',  '/data/documents/leave.txt',       6000,  2,  '员工请假申请审批流程说明',                  1,  0, 1);

-- ---------------------------
-- 4. 对话记录测试数据
-- ---------------------------
INSERT INTO tb_conversation (id, user_id, title, model_name, message_count) VALUES
(1, 2, '考勤制度相关咨询',     'qwen2.5:7b', 4),
(2, 2, 'API设计规范咨询',      'qwen2.5:7b', 2),
(3, 3, '报销流程咨询',         'qwen2.5:7b', 3);

-- ---------------------------
-- 5. 消息测试数据
-- ---------------------------
INSERT INTO tb_message (conversation_id, role, content, source_docs, tokens_used) VALUES
(1, 'user',      '请问我们公司的请假流程是怎样的？',                                          NULL,         15),
(1, 'assistant', '您好！根据公司请假制度，员工请假流程如下：\n\n1. 请假申请需提前1个工作日提交\n2. 3天以内由部门主管审批\n3. 3天以上需部门主管及HR审批\n4. 紧急情况可电话报备后补申请\n\n详细请参考《请假申请流程》文档。', '[{"doc_id":7,"title":"请假申请流程"}]', 120),
(2, 'user',      'RESTful API的URL命名应该使用单数还是复数？',                                 NULL,         12),
(2, 'assistant', 'RESTful API设计中，推荐使用复数名词作为资源名称。例如：\n- ✅ /api/users （推荐）\n- ❌ /api/user （不推荐）\n\n这样可以保持一致性，并且符合RESTful的设计理念。更多细节请参考《RESTful API设计规范》文档。', '[{"doc_id":3,"title":"RESTful API 设计规范"}]', 95),
(3, 'user',      '费用报销需要提供哪些材料？',                                                NULL,         13),
(3, 'assistant', '费用报销需要准备以下材料：\n1. 发票原件（需符合税务要求）\n2. 费用明细清单\n3. 相关审批单（如出差申请单）\n4. 合同或协议（如涉及）\n\n请确保所有材料齐全后提交至财务部。', NULL, 85);

-- ---------------------------
-- 6. 系统日志测试数据
-- ---------------------------
INSERT INTO tb_sys_log (user_id, action, detail, ip_address) VALUES
(1, 'login',  '管理员登录系统',                     '192.168.1.100'),
(2, 'login',  '用户登录系统',                       '192.168.1.101'),
(2, 'query',  '查询考勤制度相关文档',                '192.168.1.101'),
(1, 'upload', '上传文档：员工考勤管理制度',           '192.168.1.100'),
(3, 'login',  '用户登录系统',                       '192.168.1.102'),
(3, 'query',  '查询报销流程',                       '192.168.1.102'),
(1, 'login',  '管理员登录系统',                     '192.168.1.100');
