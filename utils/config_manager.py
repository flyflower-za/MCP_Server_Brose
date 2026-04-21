"""
配置持久化管理器
支持配置的加载、保存、导入、导出
"""
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# 使用标准 logging 模块
logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化配置管理器

        Args:
            config_dir: 配置目录路径，默认为 config/
        """
        if config_dir is None:
            # 默认使用项目根目录下的 config 目录
            config_dir = Path(__file__).parent.parent / "config"

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 配置文件路径
        self.servers_file = self.config_dir / "servers.json"
        self.ports_file = self.config_dir / "ports.json"
        self.settings_file = self.config_dir / "settings.json"

        logger.info(f"配置目录: {self.config_dir}")

    def load_servers(self) -> Dict[str, Any]:
        """
        加载服务器配置

        Returns:
            服务器配置字典
        """
        if not self.servers_file.exists():
            logger.info("服务器配置文件不存在，返回空配置")
            return {}

        try:
            with open(self.servers_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"已加载 {len(config)} 个服务器配置")
            return config
        except Exception as e:
            logger.error(f"加载服务器配置失败: {e}")
            return {}

    def save_servers(self, servers: Dict[str, Any]) -> bool:
        """
        保存服务器配置

        Args:
            servers: 服务器配置字典

        Returns:
            是否成功
        """
        try:
            # 创建备份
            self._backup_file(self.servers_file)

            # 保存配置
            with open(self.servers_file, 'w', encoding='utf-8') as f:
                json.dump(servers, f, indent=2, ensure_ascii=False)

            logger.info(f"已保存 {len(servers)} 个服务器配置")
            return True
        except Exception as e:
            logger.error(f"保存服务器配置失败: {e}")
            return False

    def load_ports(self) -> Dict[str, int]:
        """
        加载端口配置

        Returns:
            端口配置字典 {server_id: port}
        """
        if not self.ports_file.exists():
            logger.info("端口配置文件不存在，返回空配置")
            return {}

        try:
            with open(self.ports_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"已加载 {len(config)} 个端口配置")
            return config
        except Exception as e:
            logger.error(f"加载端口配置失败: {e}")
            return {}

    def save_ports(self, ports: Dict[str, int]) -> bool:
        """
        保存端口配置

        Args:
            ports: 端口配置字典

        Returns:
            是否成功
        """
        try:
            # 创建备份
            self._backup_file(self.ports_file)

            # 保存配置
            with open(self.ports_file, 'w', encoding='utf-8') as f:
                json.dump(ports, f, indent=2, ensure_ascii=False)

            logger.info(f"已保存 {len(ports)} 个端口配置")
            return True
        except Exception as e:
            logger.error(f"保存端口配置失败: {e}")
            return False

    def load_settings(self) -> Dict[str, Any]:
        """
        加载系统设置

        Returns:
            系统设置字典
        """
        if not self.settings_file.exists():
            logger.info("系统设置文件不存在，返回默认设置")
            return self._get_default_settings()

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            logger.info("已加载系统设置")
            return settings
        except Exception as e:
            logger.error(f"加载系统设置失败: {e}")
            return self._get_default_settings()

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        保存系统设置

        Args:
            settings: 系统设置字典

        Returns:
            是否成功
        """
        try:
            # 创建备份
            self._backup_file(self.settings_file)

            # 保存配置
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            logger.info("已保存系统设置")
            return True
        except Exception as e:
            logger.error(f"保存系统设置失败: {e}")
            return False

    def export_all(self) -> Dict[str, Any]:
        """
        导出所有配置

        Returns:
            所有配置的字典
        """
        return {
            "version": "1.0.0",
            "exported_at": datetime.now().isoformat(),
            "servers": self.load_servers(),
            "ports": self.load_ports(),
            "settings": self.load_settings(),
        }

    def import_all(self, config: Dict[str, Any], overwrite: bool = False) -> bool:
        """
        导入所有配置

        Args:
            config: 配置字典
            overwrite: 是否覆盖现有配置

        Returns:
            是否成功
        """
        try:
            # 导入服务器配置
            if "servers" in config:
                if overwrite or not self.servers_file.exists():
                    self.save_servers(config["servers"])

            # 导入端口配置
            if "ports" in config:
                if overwrite or not self.ports_file.exists():
                    self.save_ports(config["ports"])

            # 导入系统设置
            if "settings" in config:
                if overwrite or not self.settings_file.exists():
                    self.save_settings(config["settings"])

            logger.info("配置导入成功")
            return True
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False

    def _backup_file(self, file_path: Path):
        """
        备份配置文件

        Args:
            file_path: 文件路径
        """
        if not file_path.exists():
            return

        # 创建备份目录
        backup_dir = self.config_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # 备份文件名：原文件名.时间戳.bak
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{file_path.stem}_{timestamp}.bak"

        # 复制文件
        import shutil
        shutil.copy2(file_path, backup_path)
        logger.debug(f"已创建备份: {backup_path}")

        # 只保留最近 10 个备份
        self._cleanup_backups(backup_dir, file_path.stem, keep=10)

    def _cleanup_backups(self, backup_dir: Path, prefix: str, keep: int = 10):
        """
        清理旧备份文件

        Args:
            backup_dir: 备份目录
            prefix: 文件名前缀
            keep: 保留数量
        """
        backups = sorted(
            backup_dir.glob(f"{prefix}_*.bak"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # 删除超过保留数量的旧备份
        for old_backup in backups[keep:]:
            old_backup.unlink()
            logger.debug(f"已删除旧备份: {old_backup}")

    def _get_default_settings(self) -> Dict[str, Any]:
        """
        获取默认系统设置

        Returns:
            默认设置字典
        """
        return {
            "auto_restart": True,
            "max_restart_count": 3,
            "health_check_interval": 30,
            "log_level": "INFO",
            "port_allocation": {
                "base_port": 51235,
                "max_port": 51250
            }
        }

    def get_status(self) -> Dict[str, Any]:
        """
        获取配置状态

        Returns:
            配置状态信息
        """
        return {
            "config_dir": str(self.config_dir),
            "servers_config_exists": self.servers_file.exists(),
            "ports_config_exists": self.ports_file.exists(),
            "settings_config_exists": self.settings_file.exists(),
            "servers_count": len(self.load_servers()),
            "ports_count": len(self.load_ports()),
            "backups_count": len(list((self.config_dir / "backups").glob("*.bak"))) if (self.config_dir / "backups").exists() else 0
        }


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config_manager() -> ConfigManager:
    """获取配置管理器实例"""
    return config_manager
