"""
进度管理系统
支持实时任务进度跟踪和WebSocket推送
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class TaskProgress:
    """任务进度数据"""
    task_id: str
    task_type: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    current_step: str
    total_steps: int
    current_step_number: int
    created_at: datetime
    updated_at: datetime
    result: Optional[dict] = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "current_step_number": self.current_step_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata
        }


class ProgressManager:
    """进度管理器"""

    def __init__(self):
        """初始化进度管理器"""
        self.tasks: Dict[str, TaskProgress] = {}
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._cleanup_interval = 3600  # 1小时清理一次旧任务

    async def start_cleanup_task(self):
        """启动定期清理任务"""
        while True:
            await asyncio.sleep(self._cleanup_interval)
            await self._cleanup_old_tasks()

    async def _cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        cutoff_time = datetime.now() - max_age_hours * 3600
        tasks_to_remove = []

        for task_id, task in self.tasks.items():
            if task.created_at < cutoff_time:
                if task.status in ["completed", "failed"]:
                    tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self.tasks[task_id]
            if task_id in self.subscribers:
                del self.subscribers[task_id]

    def create_task(
        self,
        task_type: str,
        total_steps: int,
        metadata: Optional[dict] = None
    ) -> str:
        """创建新任务"""
        task_id = f"{task_type}_{uuid.uuid4().hex[:8]}"
        task = TaskProgress(
            task_id=task_id,
            task_type=task_type,
            status="pending",
            progress=0,
            current_step="等待开始",
            total_steps=total_steps,
            current_step_number=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=metadata or {}
        )
        self.tasks[task_id] = task
        return task_id

    def update_progress(
        self,
        task_id: str,
        step_number: int,
        message: str,
        metadata: Optional[dict] = None
    ):
        """更新任务进度"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.progress = min(100, int((step_number / task.total_steps) * 100))
        task.current_step = message
        task.current_step_number = step_number
        task.updated_at = datetime.now()
        task.status = "processing"

        if metadata:
            task.metadata.update(metadata)

        # 异步通知订阅者
        asyncio.create_task(self._notify_subscribers(task_id))
        return True

    def complete_task(self, task_id: str, result: dict, metadata: Optional[dict] = None):
        """完成任务"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = "completed"
        task.progress = 100
        task.result = result
        task.updated_at = datetime.now()

        if metadata:
            task.metadata.update(metadata)

        asyncio.create_task(self._notify_subscribers(task_id))
        return True

    def fail_task(self, task_id: str, error: str, metadata: Optional[dict] = None):
        """任务失败"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = "failed"
        task.error = error
        task.updated_at = datetime.now()

        if metadata:
            task.metadata.update(metadata)

        asyncio.create_task(self._notify_subscribers(task_id))
        return True

    async def subscribe(self, task_id: str) -> asyncio.Queue:
        """订阅任务进度更新"""
        if task_id not in self.subscribers:
            self.subscribers[task_id] = []

        queue = asyncio.Queue()
        self.subscribers[task_id].append(queue)

        # 发送当前状态
        current_progress = self.get_progress(task_id)
        if current_progress:
            await queue.put(current_progress)

        return queue

    async def unsubscribe(self, task_id: str, queue: asyncio.Queue):
        """取消订阅"""
        if task_id in self.subscribers:
            if queue in self.subscribers[task_id]:
                self.subscribers[task_id].remove(queue)

    async def _notify_subscribers(self, task_id: str):
        """通知订阅者"""
        if task_id not in self.subscribers:
            return

        progress_data = self.get_progress(task_id)
        if not progress_data:
            return

        # 通知所有订阅者
        for queue in self.subscribers[task_id]:
            try:
                await queue.put(progress_data)
            except Exception as e:
                print(f"通知订阅者失败: {e}")

    def get_progress(self, task_id: str) -> Optional[dict]:
        """获取任务进度"""
        if task_id in self.tasks:
            return self.tasks[task_id].to_dict()
        return None

    def get_all_active_tasks(self) -> List[dict]:
        """获取所有活动任务"""
        return [
            task.to_dict()
            for task in self.tasks.values()
            if task.status in ["pending", "processing"]
        ]

    def get_task_stats(self) -> dict:
        """获取任务统计"""
        total = len(self.tasks)
        pending = sum(1 for t in self.tasks.values() if t.status == "pending")
        processing = sum(1 for t in self.tasks.values() if t.status == "processing")
        completed = sum(1 for t in self.tasks.values() if t.status == "completed")
        failed = sum(1 for t in self.tasks.values() if t.status == "failed")

        return {
            "total": total,
            "pending": pending,
            "processing": processing,
            "completed": completed,
            "failed": failed
        }


# 全局实例
progress_manager = ProgressManager()