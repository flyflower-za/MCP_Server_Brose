#!/usr/bin/env python3
"""
配置持久化功能测试脚本
"""
import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.config_manager import ConfigManager


def test_config_manager():
    """测试配置管理器"""
    print("=" * 60)
    print("配置持久化功能测试")
    print("=" * 60)
    print()

    # 创建配置管理器
    config_dir = Path(__file__).parent / "config"
    manager = ConfigManager(config_dir)

    # 1. 测试服务器配置
    print("1️⃣  测试服务器配置")
    print("-" * 40)

    # 保存服务器配置
    servers_config = {
        "test_server_1": {
            "name": "Test Server 1",
            "description": "Test server for config persistence",
            "enabled": True,
            "version": "1.0.0",
            "module": "mcp_servers.test.server",
            "prefix": "/test",
            "tags": ["test"]
        }
    }

    success = manager.save_servers(servers_config)
    print(f"✅ 保存服务器配置: {success}")

    # 加载服务器配置
    loaded_servers = manager.load_servers()
    print(f"✅ 加载服务器配置: {len(loaded_servers)} 个服务器")
    assert loaded_servers == servers_config, "服务器配置不匹配"
    print()

    # 2. 测试端口配置
    print("2️⃣  测试端口配置")
    print("-" * 40)

    ports_config = {
        "test_server_1": 51240,
        "test_server_2": 51241
    }

    success = manager.save_ports(ports_config)
    print(f"✅ 保存端口配置: {success}")

    loaded_ports = manager.load_ports()
    print(f"✅ 加载端口配置: {len(loaded_ports)} 个端口")
    assert loaded_ports == ports_config, "端口配置不匹配"
    print()

    # 3. 测试系统设置
    print("3️⃣  测试系统设置")
    print("-" * 40)

    settings_config = {
        "auto_restart": True,
        "max_restart_count": 3,
        "health_check_interval": 30,
        "log_level": "INFO",
        "port_allocation": {
            "base_port": 51235,
            "max_port": 51250
        }
    }

    success = manager.save_settings(settings_config)
    print(f"✅ 保存系统设置: {success}")

    loaded_settings = manager.load_settings()
    print(f"✅ 加载系统设置: {len(loaded_settings)} 项设置")
    assert loaded_settings == settings_config, "系统设置不匹配"
    print()

    # 4. 测试配置状态
    print("4️⃣  测试配置状态")
    print("-" * 40)

    status = manager.get_status()
    print(f"✅ 配置目录: {status['config_dir']}")
    print(f"✅ 服务器配置存在: {status['servers_config_exists']}")
    print(f"✅ 端口配置存在: {status['ports_config_exists']}")
    print(f"✅ 系统设置存在: {status['settings_config_exists']}")
    print(f"✅ 服务器数量: {status['servers_count']}")
    print(f"✅ 端口配置数量: {status['ports_count']}")
    print()

    # 5. 测试导出配置
    print("5️⃣  测试导出配置")
    print("-" * 40)

    exported = manager.export_all()
    print(f"✅ 导出配置版本: {exported['version']}")
    print(f"✅ 导出时间: {exported['exported_at']}")
    print(f"✅ 包含配置类型: {list(exported.keys())}")
    assert "servers" in exported, "缺少 servers 配置"
    assert "ports" in exported, "缺少 ports 配置"
    assert "settings" in exported, "缺少 settings 配置"
    print()

    # 6. 测试配置文件
    print("6️⃣  测试配置文件")
    print("-" * 40)

    servers_file = config_dir / "servers.json"
    ports_file = config_dir / "ports.json"
    settings_file = config_dir / "settings.json"

    print(f"✅ 服务器配置文件: {servers_file.exists()}")
    print(f"✅ 端口配置文件: {ports_file.exists()}")
    print(f"✅ 系统设置文件: {settings_file.exists()}")

    # 检查备份
    backup_dir = config_dir / "backups"
    if backup_dir.exists():
        backups = list(backup_dir.glob("*.bak"))
        print(f"✅ 备份文件数量: {len(backups)}")
    print()

    # 7. 清理测试配置
    print("7️⃣  清理测试配置")
    print("-" * 40)

    # 删除测试配置文件
    if servers_file.exists():
        servers_file.unlink()
        print(f"✅ 已删除: {servers_file}")

    if ports_file.exists():
        ports_file.unlink()
        print(f"✅ 已删除: {ports_file}")

    if settings_file.exists():
        settings_file.unlink()
        print(f"✅ 已删除: {settings_file}")
    print()

    print("=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_config_manager()
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
