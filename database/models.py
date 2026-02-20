"""
数据库模型定义

从 tender-monitor-demo/main.go 的 SQL schema 迁移到 SQLAlchemy ORM
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Source(Base):
    """采集源 - 对应 sources 表"""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="采集源名称")
    code = Column(String(50), unique=True, nullable=False, comment="采集源代码")
    category = Column(String(50), nullable=False, comment="分类: province/industry/soe")
    base_url = Column(String(500), comment="基础URL")
    description = Column(Text, comment="描述")
    is_active = Column(Integer, default=1, comment="是否启用 0/1")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    traces = relationship("Trace", back_populates="source")
    tenders = relationship("Tender", back_populates="source")
    collect_tasks = relationship("CollectTask", back_populates="source")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "category": self.category,
            "base_url": self.base_url,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Trace(Base):
    """轨迹记录 - 对应 traces 表"""
    __tablename__ = "traces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"), comment="关联的采集源ID")
    name = Column(String(200), nullable=False, comment="轨迹名称")
    type = Column(String(50), nullable=False, comment="类型: list/detail")
    raw_content = Column(Text, comment="原始内容JSON")
    parsed_url = Column(String(500), comment="解析后的URL")
    status = Column(String(50), default="draft", comment="状态: draft/active")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    source = relationship("Source", back_populates="traces")

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "name": self.name,
            "type": self.type,
            "raw_content": self.raw_content,
            "parsed_url": self.parsed_url,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TagDefinition(Base):
    """标签定义 - 对应 tag_definitions 表"""
    __tablename__ = "tag_definitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, comment="标签名称")
    color = Column(String(50), comment="标签颜色")
    sort_order = Column(Integer, default=0, comment="排序")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "sort_order": self.sort_order,
        }


class CollectTask(Base):
    """采集任务 - 对应 collect_tasks 表"""
    __tablename__ = "collect_tasks"

    id = Column(String(50), primary_key=True, comment="任务ID")
    source_id = Column(Integer, ForeignKey("sources.id"), comment="采集源ID")
    source_name = Column(String(200), comment="采集源名称")
    keywords = Column(Text, comment="关键词列表（JSON）")
    status = Column(String(50), default="pending", comment="状态: pending/running/completed/failed/cancelled")
    progress = Column(Integer, default=0, comment="进度 0-100")
    found = Column(Integer, default=0, comment="找到的项目数")
    saved = Column(Integer, default=0, comment="保存的项目数")
    message = Column(Text, comment="状态消息")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    completed_at = Column(DateTime, comment="完成时间")

    # 关系
    source = relationship("Source", back_populates="collect_tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "keywords": self.keywords,
            "status": self.status,
            "progress": self.progress,
            "found": self.found,
            "saved": self.saved,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class Tender(Base):
    """招标信息 - 对应 tenders 表"""
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"), comment="采集源ID")
    title = Column(String(500), comment="标题")
    amount = Column(String(100), comment="金额")
    publish_date = Column(String(50), comment="发布日期")
    deadline = Column(String(50), comment="截止日期")
    contact = Column(String(200), comment="联系人")
    phone = Column(String(100), comment="联系电话")
    url = Column(String(1000), unique=True, comment="详情页URL（用于去重）")
    keywords = Column(Text, comment="关键词")
    content = Column(Text, comment="详细内容")
    attachments = Column(Text, comment="附件列表（JSON）")
    status = Column(String(50), default="active", comment="状态: active/archived")
    tags = Column(Text, comment="标签列表（逗号分隔）")
    note = Column(Text, comment="备注")
    reviewed_at = Column(String(50), comment="审核时间")
    reviewed_by = Column(String(100), comment="审核人")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    source = relationship("Source", back_populates="tenders")

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "title": self.title,
            "amount": self.amount,
            "publish_date": self.publish_date,
            "deadline": self.deadline,
            "contact": self.contact,
            "phone": self.phone,
            "url": self.url,
            "keywords": self.keywords,
            "content": self.content,
            "attachments": self.attachments,
            "status": self.status,
            "tags": self.tags,
            "note": self.note,
            "reviewed_at": self.reviewed_at,
            "reviewed_by": self.reviewed_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
