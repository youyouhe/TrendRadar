"""
采集任务管理器

管理异步采集任务的生命周期：创建、跟踪、取消
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional, List, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import CollectTask, Source, Tender


class TaskManager:
    """采集任务管理器"""

    def __init__(self):
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_cancellers: Dict[str, asyncio.Event] = {}

    def generate_task_id(self) -> str:
        """生成任务ID"""
        return f"task_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"

    async def create_task(
        self,
        db: AsyncSession,
        source_id: int,
        keywords: List[str],
        collector_func: Callable,
        max_items: int = 10
    ) -> str:
        """
        创建并启动采集任务

        Args:
            db: 数据库会话
            source_id: 采集源ID
            keywords: 关键词列表
            collector_func: 采集函数（异步）
            max_items: 最多采集数量

        Returns:
            任务ID
        """
        # 生成任务ID
        task_id = self.generate_task_id()

        # 查询采集源信息
        result = await db.execute(select(Source).where(Source.id == source_id))
        source = result.scalar_one_or_none()

        if not source:
            raise ValueError(f"采集源不存在: {source_id}")

        # 创建任务记录
        task = CollectTask(
            id=task_id,
            source_id=source_id,
            source_name=source.name,
            keywords=",".join(keywords),
            status="pending",
            progress=0,
            message="任务已创建，等待执行"
        )
        db.add(task)
        await db.commit()

        # 创建取消事件
        cancel_event = asyncio.Event()
        self.task_cancellers[task_id] = cancel_event

        # 启动异步任务
        async_task = asyncio.create_task(
            self._run_collect_task(
                task_id=task_id,
                db=db,
                source=source,
                keywords=keywords,
                collector_func=collector_func,
                max_items=max_items,
                cancel_event=cancel_event
            )
        )

        self.running_tasks[task_id] = async_task

        return task_id

    async def _run_collect_task(
        self,
        task_id: str,
        db: AsyncSession,
        source: Source,
        keywords: List[str],
        collector_func: Callable,
        max_items: int,
        cancel_event: asyncio.Event
    ):
        """
        执行采集任务（内部方法）

        Args:
            task_id: 任务ID
            db: 数据库会话
            source: 采集源对象
            keywords: 关键词列表
            collector_func: 采集函数
            max_items: 最多采集数量
            cancel_event: 取消事件
        """
        try:
            # 更新状态为运行中
            await self._update_task(
                db, task_id,
                status="running",
                message=f"开始采集 {source.name}"
            )

            # 定义进度回调
            async def progress_callback(progress: int, message: str):
                # 检查是否取消
                if cancel_event.is_set():
                    raise asyncio.CancelledError("任务已取消")

                # 更新进度
                await self._update_task(db, task_id, progress=progress, message=message)

            # 执行采集
            result = await collector_func(
                source_name=source.name,
                base_url=source.base_url,
                keywords=keywords,
                max_items=max_items,
                progress_callback=progress_callback
            )

            # 保存采集结果到数据库
            saved_count = await self._save_tenders(db, source.id, result.data)

            # 更新任务状态为完成
            await self._update_task(
                db, task_id,
                status="completed",
                progress=100,
                found=result.total,
                saved=saved_count,
                message=f"采集完成：找到 {result.total} 个，保存 {saved_count} 个",
                completed_at=datetime.now()
            )

        except asyncio.CancelledError:
            # 任务被取消
            await self._update_task(
                db, task_id,
                status="cancelled",
                message="任务已取消"
            )

        except Exception as e:
            # 任务失败
            await self._update_task(
                db, task_id,
                status="failed",
                message=f"采集失败: {str(e)}"
            )

        finally:
            # 清理
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            if task_id in self.task_cancellers:
                del self.task_cancellers[task_id]

    async def _update_task(
        self,
        db: AsyncSession,
        task_id: str,
        **kwargs
    ):
        """更新任务状态"""
        result = await db.execute(
            select(CollectTask).where(CollectTask.id == task_id)
        )
        task = result.scalar_one_or_none()

        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)

            task.updated_at = datetime.now()
            await db.commit()

    async def _save_tenders(
        self,
        db: AsyncSession,
        source_id: int,
        tender_data_list: List[Dict]
    ) -> int:
        """
        保存招标信息到数据库（去重）

        Args:
            db: 数据库会话
            source_id: 采集源ID
            tender_data_list: 招标信息列表

        Returns:
            保存的数量
        """
        saved_count = 0

        for data in tender_data_list:
            # 检查URL是否已存在（去重）
            url = data.get('url', '')
            if not url:
                continue

            result = await db.execute(
                select(Tender).where(Tender.url == url)
            )
            existing = result.scalar_one_or_none()

            if existing:
                # 已存在，跳过
                continue

            # 创建新记录
            tender = Tender(
                source_id=source_id,
                title=data.get('title'),
                amount=data.get('budget'),  # budget -> amount
                publish_date=data.get('publish_date'),
                deadline=data.get('deadline'),
                contact=data.get('contact_person'),
                phone=data.get('contact_phone'),
                url=url,
                keywords=data.get('category', ''),
                content=str(data.get('requirements', '')),
                status='active'
            )

            db.add(tender)
            saved_count += 1

        await db.commit()
        return saved_count

    async def cancel_task(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消
        """
        if task_id in self.task_cancellers:
            # 设置取消事件
            self.task_cancellers[task_id].set()

            # 取消异步任务
            if task_id in self.running_tasks:
                self.running_tasks[task_id].cancel()

            return True

        return False

    async def get_task_status(self, db: AsyncSession, task_id: str) -> Optional[Dict]:
        """
        查询任务状态

        Args:
            db: 数据库会话
            task_id: 任务ID

        Returns:
            任务信息字典
        """
        result = await db.execute(
            select(CollectTask).where(CollectTask.id == task_id)
        )
        task = result.scalar_one_or_none()

        if task:
            return task.to_dict()

        return None

    async def list_tasks(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        查询任务列表

        Args:
            db: 数据库会话
            status: 状态筛选（可选）
            limit: 最大返回数量

        Returns:
            任务列表
        """
        query = select(CollectTask).order_by(CollectTask.created_at.desc()).limit(limit)

        if status:
            query = query.where(CollectTask.status == status)

        result = await db.execute(query)
        tasks = result.scalars().all()

        return [task.to_dict() for task in tasks]


# 全局任务管理器实例
task_manager = TaskManager()
