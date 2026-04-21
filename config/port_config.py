"""
固定端口配置管理
使用 ConfigManager 实现配置持久化
"""
from typing import Optional, Dict
from utils.config_manager import get_config_manager


def get_all_fixed_ports() -> Dict[str, int]:
    """获取全部固定端口配置 {server_id: port}"""
    config_manager = get_config_manager()
    return config_manager.load_ports()


def get_fixed_port(server_id: str) -> Optional[int]:
    """
    获取指定服务器的固定端口，无配置则返回 None
    返回 None 时由 PortAllocator 动态分配
    """
    config_manager = get_config_manager()
    ports = config_manager.load_ports()
    return ports.get(server_id)


def set_fixed_port(server_id: str, port: int) -> None:
    """设置并持久化指定服务器的固定端口"""
    if not (1024 <= port <= 65535):
        raise ValueError(f"端口号须在 1024~65535 之间，当前: {port}")

    config_manager = get_config_manager()
    ports = config_manager.load_ports()
    ports[server_id] = port
    config_manager.save_ports(ports)


def remove_fixed_port(server_id: str) -> bool:
    """删除指定服务器的固定端口配置（恢复动态分配），返回是否存在"""
    config_manager = get_config_manager()
    ports = config_manager.load_ports()

    if server_id in ports:
        del ports[server_id]
        config_manager.save_ports(ports)
        return True

    return False
