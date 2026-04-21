"""
进程管理器单元测试
"""
import pytest
import time
import hmac
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from utils.process_manager import ProcessManager, ProcessInfo
from utils.port_allocator import PortAllocator


class TestProcessInfo:
    """ProcessInfo 测试"""

    def test_process_info_creation(self):
        """测试 ProcessInfo 创建"""
        info = ProcessInfo(
            server_id="test_server",
            pid=12345,
            port=51238,
            start_time=datetime.now()
        )

        assert info.server_id == "test_server"
        assert info.pid == 12345
        assert info.port == 51238
        assert info.restart_count == 0
        assert info.last_restart_time is None

    def test_to_dict(self):
        """测试 to_dict 方法"""
        start_time = datetime(2026, 4, 21, 12, 0, 0)
        info = ProcessInfo(
            server_id="test_server",
            pid=12345,
            port=51238,
            start_time=start_time
        )
        info.restart_count = 2
        info.last_restart_time = datetime(2026, 4, 21, 13, 0, 0)

        result = info.to_dict()

        assert result['server_id'] == "test_server"
        assert result['pid'] == 12345
        assert result['port'] == 51238
        assert result['restart_count'] == 2
        assert 'uptime_seconds' in result


class TestProcessManager:
    """ProcessManager 测试"""

    @pytest.fixture
    def process_manager(self):
        """创建 ProcessManager 实例"""
        pm = ProcessManager()
        # 清空进程字典
        pm.processes = {}
        return pm

    @pytest.fixture
    def mock_port_allocator(self):
        """模拟端口分配器"""
        allocator = Mock(spec=PortAllocator)
        allocator.allocate_port.return_value = 51238
        allocator.allocate_port.side_effect = [51238, 51239, 51240]
        return allocator

    def test_init(self, process_manager):
        """测试初始化"""
        assert isinstance(process_manager.processes, dict)
        assert len(process_manager.processes) == 0
        assert process_manager.max_restart == 3

    def test_start_server_success(self, process_manager, mock_port_allocator):
        """测试成功启动服务器"""
        process_manager.port_allocator = mock_port_allocator
        server_config = {
            'module': 'mcp_servers.pdf_extractor.server',
            'name': 'PDF Extractor'
        }

        # Mock subprocess.Popen
        with patch('utils.process_manager.subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = None  # 进程正在运行
            mock_process.pid = 12345
            mock_popen.return_value = mock_process

            success = process_manager.start_server('pdf_extractor', server_config)

            assert success is True
            assert 'pdf_extractor' in process_manager.processes
            assert process_manager.processes['pdf_extractor'].pid == 12345
            assert process_manager.processes['pdf_extractor'].port == 51238

    def test_start_server_already_running(self, process_manager, mock_port_allocator):
        """测试启动已运行的服务器"""
        process_manager.port_allocator = mock_port_allocator

        # 先添加一个运行中的服务器
        info = ProcessInfo('pdf_extractor', 12345, 51238, datetime.now())
        process_manager.processes['pdf_extractor'] = info

        server_config = {'module': 'mcp_servers.pdf_extractor.server'}

        with patch('utils.process_manager.subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process

            with patch('utils.process_manager.psutil.pid_exists', return_value=True):
                success = process_manager.start_server('pdf_extractor', server_config)

            assert success is False

    def test_start_server_port_allocation_failed(self, process_manager):
        """测试端口分配失败"""
        # Mock 端口分配失败
        mock_allocator = Mock(spec=PortAllocator)
        mock_allocator.allocate_port.return_value = None
        process_manager.port_allocator = mock_allocator

        server_config = {'module': 'mcp_servers.pdf_extractor.server'}

        success = process_manager.start_server('pdf_extractor', server_config)

        assert success is False
        assert 'pdf_extractor' not in process_manager.processes

    def test_start_server_process_failed(self, process_manager, mock_port_allocator):
        """测试进程启动失败"""
        process_manager.port_allocator = mock_port_allocator
        server_config = {'module': 'mcp_servers.pdf_extractor.server'}

        with patch('utils.process_manager.subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = 1  # 进程立即退出
            mock_process.returncode = 1
            mock_popen.return_value = mock_process

            success = process_manager.start_server('pdf_extractor', server_config)

            assert success is False

    def test_stop_server_success(self, process_manager):
        """测试成功停止服务器"""
        # 添加一个运行中的服务器
        info = ProcessInfo('pdf_extractor', 12345, 51238, datetime.now())
        process_manager.processes['pdf_extractor'] = info
        process_manager.port_allocator = Mock()

        with patch('utils.process_manager.os.kill', return_value=None):
            with patch('utils.process_manager.time.sleep', return_value=None):
                with patch('utils.process_manager.psutil.pid_exists', return_value=False):
                    success = process_manager.stop_server('pdf_extractor')

            assert success is True
            assert 'pdf_extractor' not in process_manager.processes
            process_manager.port_allocator.release_port.assert_called_once_with(51238)

    def test_stop_server_not_running(self, process_manager):
        """测试停止未运行的服务器"""
        success = process_manager.stop_server('pdf_extractor')
        assert success is False

    def test_stop_server_force(self, process_manager):
        """测试强制停止服务器"""
        info = ProcessInfo('pdf_extractor', 12345, 51238, datetime.now())
        process_manager.processes['pdf_extractor'] = info
        process_manager.port_allocator = Mock()

        with patch('utils.process_manager.os.kill', side_effect=[None, None]):
            with patch('utils.process_manager.time.sleep', return_value=None):
                # 第一次 kill 未成功，第二次强制 kill
                with patch('utils.process_manager.psutil.pid_exists', side_effect=[True, False]):
                    with patch('utils.process_manager.os.kill') as mock_kill:
                        success = process_manager.stop_server('pdf_extractor', force=True)

                        # 应该调用两次 kill（SIGTERM 和 SIGKILL）
                        assert mock_kill.call_count == 2

    def test_restart_server_success(self, process_manager, mock_port_allocator):
        """测试成功重启服务器"""
        process_manager.port_allocator = mock_port_allocator
        server_config = {'module': 'mcp_servers.pdf_extractor.server'}

        # 添加一个运行中的服务器
        info = ProcessInfo('pdf_extractor', 12345, 51238, datetime.now())
        info.restart_count = 1
        process_manager.processes['pdf_extractor'] = info

        with patch('utils.process_manager.subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = None
            mock_process.pid = 12346
            mock_popen.return_value = mock_process

            with patch('utils.process_manager.os.kill', return_value=None):
                with patch('utils.process_manager.time.sleep', return_value=None):
                    with patch('utils.process_manager.psutil.pid_exists', return_value=False):
                        success = process_manager.restart_server('pdf_extractor', server_config)

                        assert success is True
                        # 重启次数应该增加
                        assert process_manager.processes['pdf_extractor'].restart_count == 2
                        # PID 应该改变
                        assert process_manager.processes['pdf_extractor'].pid == 12346

    def test_restart_server_max_restart_exceeded(self, process_manager, mock_port_allocator):
        """测试超过最大重启次数"""
        process_manager.port_allocator = mock_port_allocator
        server_config = {'module': 'mcp_servers.pdf_extractor.server'}

        # 添加一个达到重启上限的服务器
        info = ProcessInfo('pdf_extractor', 12345, 51238, datetime.now())
        info.restart_count = 3  # 达到上限
        process_manager.processes['pdf_extractor'] = info

        success = process_manager.restart_server('pdf_extractor', server_config)

        assert success is False

    def test_restart_server_not_running(self, process_manager, mock_port_allocator):
        """测试重启未运行的服务器（应该启动）"""
        process_manager.port_allocator = mock_port_allocator
        server_config = {'module': 'mcp_servers.pdf_extractor.server'}

        with patch('utils.process_manager.subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = None
            mock_process.pid = 12345
            mock_popen.return_value = mock_process

            success = process_manager.restart_server('pdf_extractor', server_config)

            assert success is True
            assert 'pdf_extractor' in process_manager.processes

    def test_get_server_status_running(self, process_manager):
        """测试获取运行中服务器的状态"""
        info = ProcessInfo('pdf_extractor', 12345, 51238, datetime.now())
        process_manager.processes['pdf_extractor'] = info

        with patch('utils.process_manager.psutil.pid_exists', return_value=True):
            status = process_manager.get_server_status('pdf_extractor')

            assert status['status'] == 'running'
            assert status['pid'] == 12345
            assert status['port'] == 51238

    def test_get_server_status_not_running(self, process_manager):
        """测试获取未运行服务器的状态"""
        status = process_manager.get_server_status('pdf_extractor')

        assert status['status'] == 'not_running'
        assert 'message' in status

    def test_get_server_status_stopped(self, process_manager):
        """测试获取已停止服务器的状态"""
        info = ProcessInfo('pdf_extractor', 12345, 51238, datetime.now())
        process_manager.processes['pdf_extractor'] = info

        with patch('utils.process_manager.psutil.pid_exists', return_value=False):
            status = process_manager.get_server_status('pdf_extractor')

            assert status['status'] == 'stopped'
            assert 'last_info' in status

    def test_get_all_statuses(self, process_manager):
        """测试获取所有服务器状态"""
        info1 = ProcessInfo('server1', 12345, 51238, datetime.now())
        info2 = ProcessInfo('server2', 12346, 51239, datetime.now())
        process_manager.processes['server1'] = info1
        process_manager.processes['server2'] = info2

        with patch('utils.process_manager.psutil.pid_exists', return_value=True):
            statuses = process_manager.get_all_statuses()

            assert 'server1' in statuses
            assert 'server2' in statuses
            assert statuses['server1']['status'] == 'running'
            assert statuses['server2']['status'] == 'running'

    def test_health_check(self, process_manager):
        """测试健康检查"""
        info = ProcessInfo('pdf_extractor', 12345, 51238, datetime.now())
        process_manager.processes['pdf_extractor'] = info

        with patch('utils.process_manager.psutil.pid_exists', return_value=True):
            results = process_manager.health_check()

            assert 'pdf_extractor' in results
            assert results['pdf_extractor']['status'] == 'running'
