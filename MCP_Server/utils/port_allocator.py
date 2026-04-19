"""
端口分配器
用于管理和分配服务器进程的端口号
"""
import socket
from typing import Set, Optional
from utils.logger import logger


class PortAllocator:
    """端口分配器"""

    def __init__(self, base_port: int = 51235, max_port: int = 65535):
        """
        初始化端口分配器

        Args:
            base_port: 起始端口号
            max_port: 最大端口号
        """
        self.base_port = base_port
        self.max_port = max_port
        self.allocated_ports: Set[int] = set()
        self.current_port = base_port

    def is_port_available(self, port: int) -> bool:
        """
        检查端口是否可用

        Args:
            port: 端口号

        Returns:
            端口是否可用
        """
        if port in self.allocated_ports:
            return False

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('localhost', port))
                return True
        except OSError:
            return False

    def allocate_port(self, preferred_port: Optional[int] = None) -> Optional[int]:
        """
        分配一个可用端口

        Args:
            preferred_port: 首选端口号（如果可用）

        Returns:
            分配的端口号，如果无可用端口则返回None
        """
        # 如果指定了首选端口，尝试分配
        if preferred_port is not None:
            if self.is_port_available(preferred_port):
                self.allocated_ports.add(preferred_port)
                logger.debug(f"分配端口: {preferred_port} (首选)")
                return preferred_port
            else:
                logger.warning(f"首选端口 {preferred_port} 不可用")

        # 从当前端口开始查找可用端口
        port = self.current_port
        while port <= self.max_port:
            if self.is_port_available(port):
                self.allocated_ports.add(port)
                self.current_port = port + 1
                logger.debug(f"分配端口: {port}")
                return port
            port += 1

        # 如果到达最大端口，从起始端口重新开始
        port = self.base_port
        while port < self.current_port:
            if self.is_port_available(port):
                self.allocated_ports.add(port)
                self.current_port = port + 1
                logger.debug(f"分配端口: {port} (回绕)")
                return port
            port += 1

        logger.error("无可用端口")
        return None

    def release_port(self, port: int) -> bool:
        """
        释放端口

        Args:
            port: 要释放的端口号

        Returns:
            是否成功释放
        """
        if port in self.allocated_ports:
            self.allocated_ports.remove(port)
            logger.debug(f"释放端口: {port}")
            return True
        return False

    def get_allocated_ports(self) -> Set[int]:
        """
        获取所有已分配的端口

        Returns:
            已分配的端口号集合
        """
        return self.allocated_ports.copy()

    def get_status(self) -> dict:
        """
        获取分配器状态

        Returns:
            状态信息字典
        """
        return {
            "base_port": self.base_port,
            "max_port": self.max_port,
            "current_port": self.current_port,
            "allocated_count": len(self.allocated_ports),
            "allocated_ports": sorted(list(self.allocated_ports))
        }


# 全局端口分配器实例
_global_allocator: Optional[PortAllocator] = None


def get_port_allocator() -> PortAllocator:
    """
    获取全局端口分配器实例

    Returns:
        端口分配器实例
    """
    global _global_allocator
    if _global_allocator is None:
        from config import settings
        _global_allocator = PortAllocator(
            base_port=settings.PROCESS_BASE_PORT
        )
    return _global_allocator