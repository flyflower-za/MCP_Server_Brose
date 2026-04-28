"""
进程管理器
用于管理MCP服务器进程的生命周期
"""
import os
import signal
import time
import psutil
from typing import Dict, Optional, Any
from datetime import datetime
from utils.logger import logger
from utils.port_allocator import get_port_allocator
from config.port_config import get_fixed_port
from config import settings


class ProcessInfo:
    """进程信息"""

    def __init__(self, server_id: str, pid: int, port: int, start_time: datetime):
        self.server_id = server_id
        self.pid = pid
        self.port = port
        self.start_time = start_time
        self.restart_count = 0
        self.last_restart_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "server_id": self.server_id,
            "pid": self.pid,
            "port": self.port,
            "start_time": self.start_time.isoformat(),
            "restart_count": self.restart_count,
            "last_restart_time": self.last_restart_time.isoformat() if self.last_restart_time else None,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        }


class ProcessManager:
    """进程管理器"""

    def __init__(self):
        """初始化进程管理器"""
        self.processes: Dict[str, ProcessInfo] = {}
        self.port_allocator = get_port_allocator()
        self.max_restart = 3  # 最大重启次数

    def start_server(self, server_id: str, server_config: dict, retry_count: int = 0) -> bool:
        """
        启动服务器进程（支持重试）

        Args:
            server_id: 服务器ID
            server_config: 服务器配置
            retry_count: 当前重试次数（内部使用）

        Returns:
            是否成功启动
        """
        max_retries = settings.PROCESS_MAX_RESTART
        retry_delay = settings.PROCESS_START_TIMEOUT

        try:
            # 检查是否已经在运行
            if server_id in self.processes:
                if self._is_process_running(self.processes[server_id].pid):
                    logger.warning(f"服务器 {server_id} 已在运行中")
                    return True  # 已运行也算成功

            # 分配端口（优先使用固定端口配置）
            fixed_port = get_fixed_port(server_id)
            if fixed_port is not None:
                port = self.port_allocator.allocate_port(preferred_port=fixed_port)
                if port != fixed_port:
                    logger.error(
                        f"服务器 {server_id} 配置的固定端口 {fixed_port} 不可用，"
                        f"请先释放该端口或在 Dashboard 中修改端口配置"
                    )
                    if port:
                        self.port_allocator.release_port(port)

                    # 端口分配失败，尝试重试
                    if retry_count < max_retries:
                        logger.info(f"重试启动服务器 {server_id} ({retry_count + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        return self.start_server(server_id, server_config, retry_count + 1)
                    return False
            else:
                port = self.port_allocator.allocate_port()
            if port is None:
                logger.error(f"无法为服务器 {server_id} 分配端口")

                # 端口分配失败，尝试重试
                if retry_count < max_retries:
                    logger.info(f"重试启动服务器 {server_id} ({retry_count + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    return self.start_server(server_id, server_config, retry_count + 1)
                return False

            # 启动进程
            pid = self._start_process(server_id, server_config, port)
            if pid is None:
                self.port_allocator.release_port(port)

                # 进程启动失败，尝试重试
                if retry_count < max_retries:
                    logger.info(f"重试启动服务器 {server_id} ({retry_count + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    return self.start_server(server_id, server_config, retry_count + 1)
                return False

            # 验证进程是否真正启动
            if not self._is_process_running(pid):
                logger.error(f"服务器 {server_id} 进程启动后立即退出 (PID: {pid})")
                self.port_allocator.release_port(port)

                # 进程启动失败，尝试重试
                if retry_count < max_retries:
                    logger.info(f"重试启动服务器 {server_id} ({retry_count + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    return self.start_server(server_id, server_config, retry_count + 1)
                return False

            # 记录进程信息
            self.processes[server_id] = ProcessInfo(
                server_id=server_id,
                pid=pid,
                port=port,
                start_time=datetime.now()
            )

            logger.info(f"✅ 成功启动服务器 {server_id} (PID: {pid}, Port: {port})")
            return True

        except Exception as e:
            logger.error(f"启动服务器 {server_id} 失败: {str(e)}")

            # 发生异常，尝试重试
            if retry_count < max_retries:
                logger.info(f"重试启动服务器 {server_id} ({retry_count + 1}/{max_retries})")
                time.sleep(retry_delay)
                return self.start_server(server_id, server_config, retry_count + 1)
            return False

    def stop_server(self, server_id: str, force: bool = False) -> bool:
        """
        停止服务器进程

        Args:
            server_id: 服务器ID
            force: 是否强制停止

        Returns:
            是否成功停止
        """
        if server_id not in self.processes:
            logger.warning(f"服务器 {server_id} 未在运行")
            return False

        process_info = self.processes[server_id]
        try:
            # 尝试优雅停止
            if self._stop_process(process_info.pid):
                logger.info(f"✅ 成功停止服务器 {server_id}")
            elif force:
                # 强制停止
                self._kill_process(process_info.pid)
                logger.info(f"✅ 强制停止服务器 {server_id}")
            else:
                return False

            # 释放端口
            self.port_allocator.release_port(process_info.port)

            # 移除进程记录
            del self.processes[server_id]

            return True

        except Exception as e:
            logger.error(f"停止服务器 {server_id} 失败: {str(e)}")
            return False

    def restart_server(self, server_id: str, server_config: dict) -> bool:
        """
        重启服务器进程

        Args:
            server_id: 服务器ID
            server_config: 服务器配置

        Returns:
            是否成功重启
        """
        if server_id not in self.processes:
            logger.warning(f"服务器 {server_id} 未在运行，将启动新进程")
            return self.start_server(server_id, server_config)

        process_info = self.processes[server_id]

        # 检查重启次数
        if process_info.restart_count >= self.max_restart:
            logger.error(f"服务器 {server_id} 重启次数已达上限 ({self.max_restart})")
            return False

        # 停止旧进程
        old_port = process_info.port
        if not self.stop_server(server_id, force=True):
            logger.error(f"无法停止服务器 {server_id} 的旧进程")
            return False

        # 启动新进程
        if not self.start_server(server_id, server_config):
            logger.error(f"无法启动服务器 {server_id} 的新进程")
            return False

        # 更新重启计数
        new_process_info = self.processes[server_id]
        new_process_info.restart_count = process_info.restart_count + 1
        new_process_info.last_restart_time = datetime.now()

        logger.info(f"✅ 成功重启服务器 {server_id} (Port: {old_port} -> {new_process_info.port})")
        return True

    def get_server_status(self, server_id: str) -> Optional[dict]:
        """
        获取服务器状态

        Args:
            server_id: 服务器ID

        Returns:
            服务器状态信息
        """
        if server_id not in self.processes:
            return {
                "server_id": server_id,
                "status": "not_running",
                "message": "服务器未运行"
            }

        process_info = self.processes[server_id]
        is_running = self._is_process_running(process_info.pid)

        if not is_running:
            return {
                "server_id": server_id,
                "status": "stopped",
                "message": f"进程已停止 (PID: {process_info.pid})",
                "last_info": process_info.to_dict()
            }

        return {
            "server_id": server_id,
            "status": "running",
            **process_info.to_dict()
        }

    def get_all_statuses(self) -> dict:
        """
        获取所有服务器状态

        Returns:
            所有服务器状态信息
        """
        return {
            server_id: self.get_server_status(server_id)
            for server_id in self.processes.keys()
        }

    def health_check(self) -> dict:
        """
        健康检查所有服务器

        Returns:
            健康检查结果
        """
        results = {}
        for server_id in list(self.processes.keys()):
            status = self.get_server_status(server_id)
            results[server_id] = status

            # 如果进程已停止，尝试自动重启
            if status["status"] == "stopped":
                logger.warning(f"检测到服务器 {server_id} 已停止，尝试自动重启")
                # TODO: 实现自动重启逻辑

        return results

    def _start_process(self, server_id: str, server_config: dict, port: int) -> Optional[int]:
        """
        启动单个进程

        Args:
            server_id: 服务器ID
            server_config: 服务器配置
            port: 分配的端口

        Returns:
            进程PID，失败返回None
        """
        try:
            # 构建启动命令
            module_path = server_config.get("module")
            cmd = [
                "python",
                "-m",
                "utils.server_launcher",
                "--server-id", server_id,
                "--module", module_path,
                "--port", str(port)
            ]

            # 启动进程（将输出重定向到日志文件）
            import subprocess
            log_file = settings.LOG_DIR / f"{server_id}_process.log"

            process = subprocess.Popen(
                cmd,
                stdout=log_file.open('a'),
                stderr=log_file.open('a'),
                start_new_session=True
            )

            # 等待进程启动
            time.sleep(2)

            # 检查进程是否仍在运行
            if process.poll() is None:
                logger.info(f"✓ 进程启动成功，日志: {log_file}")
                return process.pid
            else:
                # 读取错误日志
                error_msg = ""
                if log_file.exists():
                    with log_file.open('r') as f:
                        # 读取最后 20 行
                        lines = f.readlines()
                        error_msg = ''.join(lines[-20:]) if lines else ""

                logger.error(f"进程启动失败，退出码: {process.returncode}")
                if error_msg:
                    logger.error(f"错误输出:\n{error_msg}")
                return None

        except Exception as e:
            logger.error(f"启动进程失败: {str(e)}")
            return None

    def _stop_process(self, pid: int) -> bool:
        """
        停止进程（优雅）

        Args:
            pid: 进程PID

        Returns:
            是否成功停止
        """
        try:
            os.kill(pid, signal.SIGTERM)
            # 等待进程结束
            for _ in range(10):  # 最多等待10秒
                time.sleep(1)
                if not self._is_process_running(pid):
                    return True
            return False
        except ProcessLookupError:
            # 进程不存在
            return True
        except Exception as e:
            logger.error(f"停止进程失败: {str(e)}")
            return False

    def _kill_process(self, pid: int) -> bool:
        """
        强制杀死进程

        Args:
            pid: 进程PID

        Returns:
            是否成功杀死
        """
        try:
            os.kill(pid, signal.SIGKILL)
            time.sleep(1)
            return not self._is_process_running(pid)
        except ProcessLookupError:
            return True
        except Exception as e:
            logger.error(f"杀死进程失败: {str(e)}")
            return False

    def _is_process_running(self, pid: int) -> bool:
        """
        检查进程是否在运行

        Args:
            pid: 进程PID

        Returns:
            进程是否在运行
        """
        try:
            return psutil.pid_exists(pid) and psutil.Process(pid).is_running()
        except Exception:
            return False

    def health_check(self, server_id: str) -> dict:
        """
        执行服务器健康检查

        Args:
            server_id: 服务器ID

        Returns:
            健康检查结果
        """
        if server_id not in self.processes:
            return {
                "server_id": server_id,
                "status": "not_running",
                "healthy": False,
                "message": "服务器未运行"
            }

        process_info = self.processes[server_id]
        is_running = self._is_process_running(process_info.pid)

        if not is_running:
            return {
                "server_id": server_id,
                "status": "dead",
                "healthy": False,
                "message": f"进程已停止 (PID: {process_info.pid})",
                "pid": process_info.pid,
                "port": process_info.port
            }

        # 检查进程是否可访问（可选：尝试连接端口）
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', process_info.port))
            sock.close()

            port_accessible = (result == 0)
        except Exception:
            port_accessible = False

        if not port_accessible:
            return {
                "server_id": server_id,
                "status": "unhealthy",
                "healthy": False,
                "message": f"进程运行但端口不可访问 (Port: {process_info.port})",
                "pid": process_info.pid,
                "port": process_info.port
            }

        return {
            "server_id": server_id,
            "status": "healthy",
            "healthy": True,
            "message": "服务器运行正常",
            "pid": process_info.pid,
            "port": process_info.port,
            "uptime_seconds": (datetime.now() - process_info.start_time).total_seconds()
        }

    def auto_restart_failed_servers(self, server_configs: dict) -> dict:
        """
        自动重启失败的服务器

        Args:
            server_configs: 服务器配置字典

        Returns:
            重启结果统计
        """
        if not settings.PROCESS_AUTO_RESTART:
            logger.info("自动重启功能已禁用")
            return {"enabled": False, "restarted": [], "failed": []}

        restarted = []
        failed = []

        for server_id in list(self.processes.keys()):
            health = self.health_check(server_id)

            if not health["healthy"]:
                # 检查是否应该重启
                if server_id in server_configs:
                    logger.warning(f"检测到服务器 {server_id} 不健康，尝试重启...")

                    if self.restart_server(server_id, server_configs[server_id]):
                        restarted.append(server_id)
                        logger.info(f"✅ 自动重启成功: {server_id}")
                    else:
                        failed.append(server_id)
                        logger.error(f"❌ 自动重启失败: {server_id}")

        return {
            "enabled": True,
            "restarted": restarted,
            "failed": failed,
            "total_checked": len(self.processes)
        }

    def get_failed_servers(self) -> list:
        """
        获取所有失败的服务器列表

        Returns:
            失败的服务器ID列表
        """
        failed = []
        for server_id in list(self.processes.keys()):
            health = self.health_check(server_id)
            if not health["healthy"]:
                failed.append(server_id)
        return failed


# 全局进程管理器实例
_global_manager: Optional[ProcessManager] = None


def get_process_manager() -> ProcessManager:
    """
    获取全局进程管理器实例

    Returns:
        进程管理器实例
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = ProcessManager()
    return _global_manager