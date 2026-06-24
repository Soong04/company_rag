# ============================================================================
# 数据库初始化和测试数据导入脚本
# 用法: python init_db.py
# ============================================================================
import os
import sys
from app import create_app, db
from models import User, Category, Document
from models.user import User
from models.knowledge import Category, Document
from md5_util import hash_password


def init_database():
    """初始化数据库并导入测试数据"""
    app = create_app()

    with app.app_context():
        print('[*] Starting database initialization...')

        # 创建所有表
        db.create_all()
        print('[OK] Tables created')

        # ---- 检查是否已有数据 ----
        if User.query.first():
            print('[!] Database already has data, skipping import')
            return

        # ---- 导入测试数据 ----

        # 1. 用户数据
        default_pwd = hash_password('123456')
        users_data = [
            User(username='admin', password=default_pwd, real_name='System Admin',
                 email='admin@company.com', phone='13800000001', role='admin', status=1),
            User(username='zhangsan', password=default_pwd, real_name='Zhang San',
                 email='zhangsan@company.com', phone='13800000002', role='user', status=1),
            User(username='lisi', password=default_pwd, real_name='Li Si',
                 email='lisi@company.com', phone='13800000003', role='user', status=1),
            User(username='wangwu', password=default_pwd, real_name='Wang Wu',
                 email='wangwu@company.com', phone='13800000004', role='user', status=1),
            User(username='zhaoliu', password=default_pwd, real_name='Zhao Liu',
                 email='zhaoliu@company.com', phone='13800000005', role='user', status=0),
        ]
        db.session.add_all(users_data)
        db.session.flush()
        print(f'[OK] Added {len(users_data)} users')

        # 创建测试文档内容文件
        content_dir = os.path.join(app.root_path, 'data', 'documents')
        os.makedirs(content_dir, exist_ok=True)

        test_docs = {
            'attendance.txt': """Company Attendance Management Policy

Chapter 1 General Provisions
Article 1 This policy is formulated to strengthen attendance management and regulate employee attendance behavior.
Article 2 This policy applies to all employees.

Chapter 2 Attendance Rules
Article 3 The company implements an 8-hour workday: 9:00-12:00, 13:00-18:00.
Article 4 Employees should arrive and leave on time. Late arrivals within 30 minutes are fined 50 yuan.
Article 5 Business trips require prior approval from the department supervisor.

Chapter 3 Leave System
Article 6 Leave applications must be submitted 1 working day in advance.
Article 7 Leave within 3 days is approved by the department supervisor; beyond 3 days requires HR approval.
Article 8 Emergency situations can be reported by phone, with formal procedures completed within 3 days.

Chapter 4 Overtime Management
Article 9 Overtime requires advance application and departmental approval.
Article 10 Overtime pay: weekday 150%, rest day 200%.
""",
            'security.txt': """Company Information Security Policy

Chapter 1 General Provisions
Article 1 This policy is formulated to ensure information security and prevent data leakage.
Article 2 This policy applies to all information systems and network devices.

Chapter 2 Password Management
Article 3 Employees should change passwords regularly, minimum 8 characters with letters and numbers.
Article 4 Sharing account passwords with others is prohibited.

Chapter 3 Data Security
Article 5 Important data should be backed up every 7 days.
Article 6 Customer privacy data must be encrypted during storage and transmission.
Article 7 Data access for departing employees must be revoked immediately.

Chapter 4 Network Management
Article 8 The company network is divided into internal and external networks.
Article 9 Setting up unauthorized wireless networks is strictly prohibited.
""",
            'api_design.txt': """RESTful API Design Standards

1. Naming Conventions
- Use lowercase letters and hyphens for URL paths
- Use plural nouns for resource collections
- Recommended:
  [OK] GET /api/users
  [OK] GET /api/users/123
  [OK] POST /api/users
  [OK] PUT /api/users/123
  [OK] DELETE /api/users/123

2. Request Standards
- Use standard HTTP methods: GET, POST, PUT, DELETE
- Query parameters use camelCase
- Pagination uses page and size parameters

3. Response Standards
- Unified JSON format
- Paginated: {"data": [...], "total": 100, "page": 1, "size": 20}
- Error: {"code": 400, "message": "Error description"}
""",
            'product_guide.txt': """Product User Guide V3.0

Chapter 1 Overview
This product is an enterprise knowledge management platform supporting document management, smart search, and Q&A.

Chapter 2 Quick Start
1. Log in with your employee account
2. Browse knowledge documents by category
3. Ask questions in the Q&A page for automatic knowledge retrieval

Chapter 3 Main Features
3.1 Document Management
- Supports PDF, Word, TXT, Markdown formats
- Category management and full-text search
- Document version management

3.2 Smart Search
- Semantic search understanding user intent
- Keyword highlighting
- Results sorted by relevance

3.3 Q&A System
- RAG-based technology for accurate answers
- Traceable source citations
- Historical conversation records
""",
            'recruit_plan.txt': """2024 Recruitment Plan

I. Overall Target
Plan to recruit 50 people in 2024, focusing on R&D and marketing positions.

II. Position Requirements
1. Technology R&D (25 people)
   - Senior Java Engineer: 5
   - Frontend Developer: 5
   - Test Engineer: 3
   - DevOps Engineer: 2
   - Data Analyst: 3
   - Product Manager: 3
   - UI/UX Designer: 4

2. Marketing (15 people)
   - Marketing Manager: 2
   - Sales Representative: 8
   - Customer Success Manager: 5

3. Functions (10 people)
   - HR Specialist: 3
   - Finance Specialist: 2
   - Admin Specialist: 2
   - Legal Specialist: 3

III. Schedule
Q1: 20, Q2: 15, Q3: 10, Q4: 5
""",
            'expense.txt': """Expense Reimbursement Policy

I. Process
1. Employee fills out reimbursement form with all receipts
2. Department supervisor reviews for reasonableness
3. Finance reviews invoice compliance
4. GM approval (amounts over 5000 yuan)
5. Finance arranges payment

II. Standards
1. Travel: 200 yuan/day per diem
2. Transportation: actual cost with receipts
3. Meals: entertainment meals max 200 yuan/person
4. Office supplies: max 2000 yuan per order

III. Notes
1. All invoices must be official with company name
2. Submit within 30 days of expense occurrence
3. False claims will be seriously handled
""",
            'leave.txt': """Leave Application Process

I. Leave Types
1. Annual Leave: 5 days for employees with 1+ year service
2. Sick Leave: Hospital certificate required
3. Personal Leave: For personal matters
4. Marriage Leave: 7 days for legal marriage age
5. Maternity Leave: 98 days

II. Approval Process
1. Submit application in system
2. Select leave type and time period
3. Fill in reason
4. System routes approval based on days
5. System notifies employee upon approval

III. Notes
1. Apply in advance, emergency can be phone-reported
2. Report back after leave ends
3. Failure to follow procedure = absenteeism
""",
        }

        for filename, content in test_docs.items():
            filepath = os.path.join(content_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

        # 2. 分类数据
        categories_data = [
            Category(id=1, name='Company Policy', parent_id=0, sort_order=1,
                     description='Internal rules and employee handbook'),
            Category(id=2, name='Technical Docs', parent_id=0, sort_order=2,
                     description='Technical solutions, development standards'),
            Category(id=3, name='Product Manual', parent_id=0, sort_order=3,
                     description='Product instructions and features'),
            Category(id=4, name='HR', parent_id=0, sort_order=4,
                     description='Recruitment, training, performance'),
            Category(id=5, name='Finance', parent_id=0, sort_order=5,
                     description='Reimbursement, budget, financial policies'),
            Category(id=6, name='Attendance', parent_id=4, sort_order=1,
                     description='Attendance management and leave'),
            Category(id=7, name='Recruitment', parent_id=4, sort_order=2,
                     description='Interview process and standards'),
            Category(id=8, name='Backend', parent_id=2, sort_order=1,
                     description='Backend development standards'),
            Category(id=9, name='Frontend', parent_id=2, sort_order=2,
                     description='Frontend development standards'),
        ]
        db.session.add_all(categories_data)
        db.session.flush()
        print(f'[OK] Added {len(categories_data)} categories')

        # 3. 文档数据
        def _read_content(filepath):
            """读取测试文档文件内容"""
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return ''

        documents_data = [
            Document(id=1, category_id=1, title='Attendance Management Policy',
                     file_type='txt', file_path=os.path.join(content_dir, 'attendance.txt'),
                     file_size=os.path.getsize(os.path.join(content_dir, 'attendance.txt')),
                     page_count=5, content_summary='Company attendance, leave, overtime management',
                     content=_read_content(os.path.join(content_dir, 'attendance.txt')),
                     status=2, chunk_count=10, upload_user_id=1),
            Document(id=2, category_id=1, title='Information Security Policy',
                     file_type='txt', file_path=os.path.join(content_dir, 'security.txt'),
                     file_size=os.path.getsize(os.path.join(content_dir, 'security.txt')),
                     page_count=7, content_summary='Information security requirements and procedures',
                     content=_read_content(os.path.join(content_dir, 'security.txt')),
                     status=2, chunk_count=14, upload_user_id=1),
            Document(id=3, category_id=2, title='RESTful API Design Standards',
                     file_type='txt', file_path=os.path.join(content_dir, 'api_design.txt'),
                     file_size=os.path.getsize(os.path.join(content_dir, 'api_design.txt')),
                     page_count=6, content_summary='RESTful API design principles and naming conventions',
                     content=_read_content(os.path.join(content_dir, 'api_design.txt')),
                     status=2, chunk_count=12, upload_user_id=2),
            Document(id=4, category_id=3, title='Product User Guide V3.0',
                     file_type='txt', file_path=os.path.join(content_dir, 'product_guide.txt'),
                     file_size=os.path.getsize(os.path.join(content_dir, 'product_guide.txt')),
                     page_count=9, content_summary='Product features and operation instructions',
                     content=_read_content(os.path.join(content_dir, 'product_guide.txt')),
                     status=2, chunk_count=18, upload_user_id=2),
            Document(id=5, category_id=4, title='2024 Recruitment Plan',
                     file_type='txt', file_path=os.path.join(content_dir, 'recruit_plan.txt'),
                     file_size=os.path.getsize(os.path.join(content_dir, 'recruit_plan.txt')),
                     page_count=3, content_summary='Department recruitment plans and requirements',
                     content=_read_content(os.path.join(content_dir, 'recruit_plan.txt')),
                     status=2, chunk_count=6, upload_user_id=1),
            Document(id=6, category_id=5, title='Expense Reimbursement Policy',
                     file_type='txt', file_path=os.path.join(content_dir, 'expense.txt'),
                     file_size=os.path.getsize(os.path.join(content_dir, 'expense.txt')),
                     page_count=4, content_summary='Expense reimbursement process and standards',
                     content=_read_content(os.path.join(content_dir, 'expense.txt')),
                     status=1, chunk_count=0, upload_user_id=3),
            Document(id=7, category_id=6, title='Leave Application Process',
                     file_type='txt', file_path=os.path.join(content_dir, 'leave.txt'),
                     file_size=os.path.getsize(os.path.join(content_dir, 'leave.txt')),
                     page_count=2, content_summary='Employee leave application and approval process',
                     content=_read_content(os.path.join(content_dir, 'leave.txt')),
                     status=1, chunk_count=0, upload_user_id=1),
        ]
        db.session.add_all(documents_data)
        db.session.flush()
        print(f'[OK] Added {len(documents_data)} documents')

        # 4. 对话记录
        from app import Conversation
        conversations_data = [
            Conversation(id=1, user_id=2, title='Attendance Policy Inquiry',
                         model_name='qwen2.5:7b', message_count=4),
            Conversation(id=2, user_id=2, title='API Design Standards Inquiry',
                         model_name='qwen2.5:7b', message_count=2),
            Conversation(id=3, user_id=3, title='Reimbursement Process Inquiry',
                         model_name='qwen2.5:7b', message_count=3),
        ]
        db.session.add_all(conversations_data)
        db.session.flush()
        print(f'[OK] Added {len(conversations_data)} conversations')

        # 5. 消息数据
        from app import Message
        import json
        messages_data = [
            Message(conversation_id=1, role='user', content='What is our company leave process?',
                    tokens_used=15),
            Message(conversation_id=1, role='assistant',
                    content='According to company policy:\n\n1. Submit application 1 working day in advance\n2. Within 3 days: department supervisor approval\n3. Over 3 days: supervisor + HR approval\n4. Emergency: phone report, then formal procedure\n\nSee "Leave Application Process" document.',
                    source_docs=json.dumps([{"doc_id": 7, "title": "Leave Application Process"}], ensure_ascii=False),
                    tokens_used=120),
            Message(conversation_id=2, role='user', content='Should RESTful API URLs use singular or plural?',
                    tokens_used=12),
            Message(conversation_id=2, role='assistant',
                    content='RESTful API design recommends plural nouns:\n- [OK] /api/users (recommended)\n- [NO] /api/user (not recommended)\n\nThis maintains consistency with RESTful principles. See "RESTful API Design Standards".',
                    source_docs=json.dumps([{"doc_id": 3, "title": "RESTful API Design Standards"}], ensure_ascii=False),
                    tokens_used=95),
            Message(conversation_id=3, role='user', content='What documents are needed for reimbursement?',
                    tokens_used=13),
            Message(conversation_id=3, role='assistant',
                    content='Required materials:\n1. Original invoices\n2. Expense details\n3. Approval forms (e.g., travel applications)\n4. Contracts/agreements (if applicable)\n\nSubmit all materials to Finance Department.',
                    tokens_used=85),
        ]
        db.session.add_all(messages_data)
        db.session.flush()
        print(f'[OK] Added {len(messages_data)} messages')

        # 6. 系统日志
        from app import SysLog
        logs_data = [
            SysLog(user_id=1, action='login', detail='Admin logged in', ip_address='192.168.1.100'),
            SysLog(user_id=2, action='login', detail='User logged in', ip_address='192.168.1.101'),
            SysLog(user_id=2, action='query', detail='Queried attendance documents', ip_address='192.168.1.101'),
            SysLog(user_id=1, action='upload', detail='Uploaded: Attendance Policy', ip_address='192.168.1.100'),
            SysLog(user_id=3, action='login', detail='User logged in', ip_address='192.168.1.102'),
            SysLog(user_id=3, action='query', detail='Queried reimbursement process', ip_address='192.168.1.102'),
            SysLog(user_id=1, action='login', detail='Admin logged in', ip_address='192.168.1.100'),
        ]
        db.session.add_all(logs_data)
        db.session.flush()
        print(f'[OK] Added {len(logs_data)} system logs')

        # 提交所有数据
        db.session.commit()
        print('\n[*] Database initialization complete!')
        print('[*] Test accounts:')
        print('    Admin - admin / 123456')
        print('    User  - zhangsan / 123456')
        print('    User  - lisi / 123456')
        print('    User  - wangwu / 123456')
        print('    Disabled - zhaoliu / 123456')


if __name__ == '__main__':
    init_database()
