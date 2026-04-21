"""
pytest 配置和 fixtures
"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_settings():
    """模拟配置"""
    from config import settings
    return settings


@pytest.fixture
def temp_log_dir(tmp_path):
    """临时日志目录"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir
