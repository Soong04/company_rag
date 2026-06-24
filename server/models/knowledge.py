# ============================================================================
# 知识库数据模型
# Category（分类）、Document（文档元信息）
# ============================================================================
from . import db


class Category(db.Model):
    """知识库分类模型"""
    __tablename__ = 'tb_category'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   comment='分类ID，主键自增')
    name = db.Column(db.String(128), nullable=False,
                     comment='分类名称')
    parent_id = db.Column(db.Integer, default=0,
                          comment='父分类ID，0表示顶级分类')
    sort_order = db.Column(db.Integer, nullable=False, default=0,
                           comment='排序顺序')
    description = db.Column(db.String(500), default=None,
                            comment='分类描述')
    create_time = db.Column(db.DateTime, nullable=False,
                            default=db.func.current_timestamp(),
                            comment='创建时间')
    update_time = db.Column(db.DateTime, nullable=False,
                            default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp(),
                            comment='更新时间')

    # 关系 - backref 自动创建 Document.category
    documents = db.relationship('Document', backref='category', lazy='dynamic',
                                cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Category {self.name}>'

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
            'description': self.description,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S'),
        }


class Document(db.Model):
    """文档元信息模型"""
    __tablename__ = 'tb_document'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   comment='文档ID，主键自增')
    category_id = db.Column(db.Integer, db.ForeignKey('tb_category.id'), nullable=False,
                            comment='所属分类ID，关联 tb_category.id')
    title = db.Column(db.String(255), nullable=False,
                      comment='文档标题')
    file_type = db.Column(db.String(20), default=None,
                          comment='文件类型（pdf/docx/txt等）')
    file_path = db.Column(db.String(500), default=None,
                          comment='文件存储路径')
    file_size = db.Column(db.BigInteger, default=0,
                          comment='文件大小（字节）')
    page_count = db.Column(db.Integer, default=0,
                           comment='文档页数/文本块数')
    content_summary = db.Column(db.String(500), default=None,
                                comment='内容摘要')
    content = db.Column(db.Text, default=None,
                        comment='文档完整内容（全文搜索用）')
    status = db.Column(db.Integer, nullable=False, default=0,
                       comment='处理状态：0=待处理，1=处理中，2=已完成，-1=失败')
    chunk_count = db.Column(db.Integer, default=0,
                            comment='文本块数量（Chroma中的分块数）')
    upload_user_id = db.Column(db.Integer, db.ForeignKey('tb_user.id'), nullable=False,
                               comment='上传用户ID，关联 tb_user.id')
    create_time = db.Column(db.DateTime, nullable=False,
                            default=db.func.current_timestamp(),
                            comment='创建时间')
    update_time = db.Column(db.DateTime, nullable=False,
                            default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp(),
                            comment='更新时间')

    def __repr__(self):
        return f'<Document {self.title}>'

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'category_id': self.category_id,
            'title': self.title,
            'file_type': self.file_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'page_count': self.page_count,
            'content_summary': self.content_summary,
            'status': self.status,
            'chunk_count': self.chunk_count,
            'upload_user_id': self.upload_user_id,
            'category_name': self.category.name if self.category else None,
            'uploader_name': self.uploader.username if self.uploader else None,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def to_search_dict(self, keyword: str = '') -> dict:
        """搜索用字典，包含高亮片段"""
        result = self.to_dict()
        if keyword and self.content:
            # 在内容中查找匹配片段
            import re
            idx = self.content.lower().find(keyword.lower())
            if idx >= 0:
                start = max(0, idx - 60)
                end = min(len(self.content), idx + len(keyword) + 60)
                snippet = self.content[start:end]
                # 替换关键词为高亮（前后各加一个空格以便前端识别）
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                snippet = pattern.sub(f'<em>{keyword}</em>', snippet)
                if start > 0:
                    snippet = '...' + snippet
                if end < len(self.content):
                    snippet = snippet + '...'
                result['snippet'] = snippet
            else:
                result['snippet'] = (self.content[:200] + '...') if self.content else ''
        else:
            result['snippet'] = self.content_summary or ''
        return result
