"""
固定端口配置管理
读写 config/server_ports.json，提供运行时的固定端口查询与持久化
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict

_PORTS_FILE = Path(__file__).parent / "server_ports.json"


def _load() -> Dict[str, int]:
    """从磁盘加载端口配置"""
    try:
        if _PORTS_FILE.exists():
            with open(_PORTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save(data: Dict[str, int]) -> None:
    """持久化端口配置到磁盘"""
    _PORTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_PORTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_all_fixed_ports() -> Dict[str, int]:
    """获取全部固定端口配置 {server_id: port}"""
    return _load()


def get_fixed_port(server_id: str) -> Optional[int]:
    """
    获取指定服务器的固定端口，无配置则返回 None
    返回 None 时由 PortAllocator 动态分配
    """
    return _load().get(server_id)


def set_fixed_port(server_id: str, port: int) -> None:
    """设置并持久化指定服务器的固定端口"""
    if not (1024 <= port <= 65535):
        raise ValueError(f"端口号须在 1024~65535 之间，当前: {port}")
    data = _load()
    data[server_id] = port
    _save(data)


def remove_fixed_port(server_id: str) -> bool:
    """删除指定服务器的固定端口配置（恢复动态分配），返回是否存在"""
    data = _load()
    if server_id in data:
        del data[server_id]
        _save(data)
        return True
    return False
