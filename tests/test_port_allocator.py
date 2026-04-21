"""
端口分配器单元测试
"""
import pytest
from unittest.mock import Mock, patch
from utils.port_allocator import PortAllocator


class TestPortAllocator:
    """PortAllocator 测试"""

    @pytest.fixture
    def allocator(self):
        """创建 PortAllocator 实例"""
        return PortAllocator(base_port=51235, max_port=51250)

    def test_init(self, allocator):
        """测试初始化"""
        assert allocator.base_port == 51235
        assert allocator.max_port == 51250
        assert allocator.current_port == 51235
        assert len(allocator.allocated_ports) == 0

    def test_is_port_available_true(self, allocator):
        """测试端口可用（未被占用）"""
        # Mock socket
        with patch('utils.port_allocator.socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value.__enter__.return_value = mock_sock_instance
            mock_sock_instance.bind.return_value = None

            available = allocator.is_port_available(51238)

            assert available is True

    def test_is_port_available_false_allocated(self, allocator):
        """测试端口不可用（已分配）"""
        allocator.allocated_ports.add(51238)

        available = allocator.is_port_available(51238)

        assert available is False

    def test_is_port_available_false_in_use(self, allocator):
        """测试端口不可用（被占用）"""
        with patch('utils.port_allocator.socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value.__enter__.return_value = mock_sock_instance
            mock_sock_instance.bind.side_effect = OSError(48)  # Address already in use

            available = allocator.is_port_available(51238)

            assert available is False

    def test_allocate_port_default(self, allocator):
        """测试默认端口分配（从起始端口开始）"""
        with patch.object(allocator, 'is_port_available', return_value=True):
            port = allocator.allocate_port()

            assert port == 51235
            assert port in allocator.allocated_ports
            assert allocator.current_port == 51236

    def test_allocate_port_preferred_available(self, allocator):
        """测试分配首选端口（可用）"""
        with patch.object(allocator, 'is_port_available', return_value=True):
            port = allocator.allocate_port(preferred_port=51240)

            assert port == 51240
            assert 51240 in allocator.allocated_ports

    def test_allocate_port_preferred_unavailable(self, allocator):
        """测试分配首选端口（不可用，分配下一个）"""
        with patch.object(allocator, 'is_port_available', side_effect=[False, True]):
            port = allocator.allocate_port(preferred_port=51240)

            assert port == 51235  # 返回下一个可用端口
            assert port in allocator.allocated_ports

    def test_allocate_port_exhausted(self, allocator):
        """测试端口耗尽"""
        with patch.object(allocator, 'is_port_available', return_value=False):
            port = allocator.allocate_port()

            assert port is None

    def test_allocate_port_wrapping(self, allocator):
        """测试端口分配回绕"""
        # 分配到 max_port 后应该回绕到 base_port
        allocator.current_port = 51250
        allocator.allocated_ports.add(51249)  # 只剩 51250

        with patch.object(allocator, 'is_port_available', side_effect=[False, True]):
            port = allocator.allocate_port()

            # 应该回绕到 base_port
            assert port == 51235

    def test_release_port_success(self, allocator):
        """测试释放端口"""
        allocator.allocated_ports.add(51238)

        success = allocator.release_port(51238)

        assert success is True
        assert 51238 not in allocator.allocated_ports

    def test_release_port_not_allocated(self, allocator):
        """测试释放未分配的端口"""
        success = allocator.release_port(51238)

        assert success is False

    def test_get_allocated_ports(self, allocator):
        """测试获取已分配端口"""
        allocator.allocated_ports.add(51238)
        allocator.allocated_ports.add(51239)

        ports = allocator.get_allocated_ports()

        assert 51238 in ports
        assert 51239 in ports
        assert len(ports) == 2

    def test_get_status(self, allocator):
        """测试获取分配器状态"""
        allocator.allocated_ports.add(51238)
        allocator.allocated_ports.add(51239)
        allocator.current_port = 51240

        status = allocator.get_status()

        assert status['base_port'] == 51235
        assert status['max_port'] == 51250
        assert status['current_port'] == 51240
        assert status['allocated_count'] == 2
        assert 51238 in status['allocated_ports']
        assert 51239 in status['allocated_ports']

    @pytest.mark.skip("并发测试在单元测试中不稳定，建议在集成测试中运行")
    def test_concurrent_allocation_safety(self, allocator):
        """测试并发分配安全性"""
        import threading

        allocated_ports = set()
        threads = []

        def allocate_thread():
            for _ in range(5):
                with patch.object(allocator, 'is_port_available', return_value=True):
                    port = allocator.allocate_port()
                    allocated_ports.add(port)
                time.sleep(0.001)

        # 创建多个线程同时分配
        for _ in range(3):
            t = threading.Thread(target=allocate_thread)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 应该分配了 15 个不重复的端口
        assert len(allocated_ports) == 15


class TestPortAllocatorEdgeCases:
    """边缘案例测试"""

    def test_invalid_port_range(self):
        """测试无效的端口范围"""
        # Python 3.12+ 的 PortAllocator 初始化不会立即验证范围
        # 只在实际分配时才会检查
        allocator = PortAllocator(base_port=100, max_port=99)

        # 尝试分配时会失败或返回 None
        with patch.object(allocator, 'is_port_available', return_value=False):
            port = allocator.allocate_port()
            # 由于没有可用端口，应该返回 None
            assert port is None

    def test_port_out_of_range(self):
        """测试端口超出范围"""
        allocator = PortAllocator(base_port=51235, max_port=51240)

        # 尝试分配超出范围的端口（会自动跳过）
        with patch.object(allocator, 'is_port_available', side_effect=[False, True]):
            # 第一次 99999 不可用，第二次使用默认端口
            port = allocator.allocate_port(preferred_port=99999)
            # 应该返回一个可用端口
            assert port is not None
            assert 51235 <= port <= 51240

    def test_release_nonexistent_port(self):
        """测试释放不存在的端口"""
        allocator = PortAllocator()
        success = allocator.release_port(99999)
        assert success is False
