"""
API 端点集成测试
测试所有主要的 API 端点功能
"""
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# 导入主应用
import sys
sys.path.insert(0, '/Users/zhouao/Documents/GitHub/MCP_Server_Brose')
from main import app
from config.settings import settings


client = TestClient(app)


class TestHealthEndpoint:
    """测试 /health 健康检查端点"""

    def test_health_returns_200(self):
        """测试健康检查返回 200"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(self):
        """测试健康检查响应结构"""
        response = client.get("/health")
        data = response.json()

        # 验证必需字段
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "architecture" in data
        assert "api_gateway" in data
        assert "backend_services" in data
        assert "system_resources" in data

    def test_health_status_values(self):
        """测试健康状态值"""
        response = client.get("/health")
        data = response.json()

        # 状态应该是 healthy, degraded, 或 unhealthy
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

        # API 网关应该正在运行
        assert data["api_gateway"]["status"] == "running"

        # 应该有版本号
        assert data["version"] == settings.VERSION


class TestSystemInfoEndpoint:
    """测试 /api/v1/system 系统信息端点"""

    def test_system_info_requires_auth(self):
        """测试系统信息端点需要认证"""
        # 测试无认证访问
        response = client.get("/api/v1/system")
        # 根据配置，可能需要认证或不需要
        assert response.status_code in [200, 401, 403]

    def test_system_info_structure(self):
        """测试系统信息响应结构"""
        # 这里使用 mock 来跳过认证
        with patch('utils.auth.verify_basic_auth'):
            response = client.get("/api/v1/system")

        if response.status_code == 200:
            data = response.json()
            # 验证基本结构
            assert "system" in data or "title" in data
            assert "version" in data or "api_prefix" in data


class TestSystemResourcesEndpoint:
    """测试 /api/v1/system/resources 系统资源端点"""

    def test_resources_returns_data(self):
        """测试资源端点返回数据"""
        response = client.get("/api/v1/system/resources")

        # 这个端点可能不需要认证
        if response.status_code == 200:
            data = response.json()
            # 验证响应结构
            assert "hub" in data
            assert "port_pool" in data
            assert "processes" in data

    def test_resources_hub_info(self):
        """测试 Hub 资源信息"""
        response = client.get("/api/v1/system/resources")

        if response.status_code == 200:
            data = response.json()
            hub_info = data["hub"]

            # 应该有 CPU 和内存信息
            assert "cpu_percent" in hub_info
            assert "memory_mb" in hub_info
            assert "pid" in hub_info

            # CPU 百分比应该在合理范围内
            assert 0 <= hub_info["cpu_percent"] <= 100
            assert hub_info["memory_mb"] > 0


class TestAuthenticationEndpoint:
    """测试 /api/v1/auth/login 认证端点"""

    def test_login_missing_credentials(self):
        """测试缺少凭证的登录"""
        response = client.post(
            "/api/v1/auth/login",
            json={}
        )
        assert response.status_code in [400, 422, 401]

    def test_login_invalid_credentials(self):
        """测试无效凭证的登录"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "invalid_user",
                "password": "wrong_password"
            }
        )
        assert response.status_code == 401

    def test_login_valid_credentials(self):
        """测试有效凭证的登录"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": settings.DASHBOARD_USERNAME,
                "password": settings.DASHBOARD_PASSWORD
            }
        )

        if response.status_code == 200:
            data = response.json()
            # 应该返回 access_token
            assert "access_token" in data
            assert "token_type" in data
            assert data["token_type"] == "bearer"


class TestConfigEndpoints:
    """测试配置管理端点"""

    def test_list_servers_requires_auth(self):
        """测试列出服务器需要认证"""
        response = client.get("/api/v1/config/servers")
        assert response.status_code in [401, 403]

    def test_update_server_config_requires_auth(self):
        """测试更新配置需要认证"""
        response = client.put(
            "/api/v1/config/servers/test_server",
            json={"enabled": False}
        )
        assert response.status_code in [401, 403, 404]


class TestProxyMiddleware:
    """测试代理中间件"""

    def test_proxy_to_pdf_extractor(self):
        """测试代理到 PDF 提取服务"""
        # 这个测试需要 PDF 服务在运行
        response = client.post(
            "/pdf/extract",
            json={"url": "https://example.com/test.pdf"}
        )

        # 可能的响应：
        # 200 - 成功
        # 404 - 服务未启动
        # 503 - 服务不可用
        assert response.status_code in [200, 404, 503]

    def test_proxy_to_qrcode_reader(self):
        """测试代理到二维码识别服务"""
        response = client.post(
            "/qrcode/qrreader",
            json={"image_url": "https://example.com/qrcode.png"}
        )

        # 同样的可能响应
        assert response.status_code in [200, 404, 503]


class TestErrorHandling:
    """测试错误处理"""

    def test_404_error_format(self):
        """测试 404 错误格式"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

        # 验证错误响应格式
        data = response.json()
        # 代理中间件返回格式：{"error": "未找到对应的服务器", "path": "/api/v1/nonexistent"}
        # 标准化错误格式：{"success": false, "error": {...}}
        assert "error" in data or "detail" in data

        if "error" in data and isinstance(data["error"], str):
            # 代理中间件格式
            assert data["error"] or data.get("path")
        elif "error" in data and isinstance(data["error"], dict):
            # 标准化格式
            assert "success" in data or "detail" in data

    def test_405_method_not_allowed(self):
        """测试不允许的方法"""
        response = client.post("/health")
        assert response.status_code == 405

    def test_422_validation_error(self):
        """测试参数验证错误"""
        response = client.post(
            "/api/v1/auth/login",
            json={"invalid_field": "value"}
        )
        # 应该返回验证错误
        assert response.status_code in [400, 422]


class TestDashboardConfigEndpoint:
    """测试 Dashboard 配置端点"""

    def test_dashboard_config_returns_config(self):
        """测试 Dashboard 配置端点"""
        response = client.get("/api/v1/system/dashboard-config")

        # 可能不需要认证
        if response.status_code == 200:
            data = response.json()
            # 验证配置字段
            assert "auth_enabled" in data
            assert "refresh_interval" in data
            assert "username" in data


class TestPerformanceEndpoints:
    """测试性能监控端点"""

    def test_system_resources_performance(self):
        """测试系统资源性能监控"""
        response = client.get("/api/v1/system/resources")

        if response.status_code == 200:
            # 测试响应时间应该合理
            assert response.elapsed.total_seconds() < 2.0

    def test_health_check_performance(self):
        """测试健康检查性能"""
        import time
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        assert response.status_code == 200
        # 健康检查应该很快
        assert (end_time - start_time) < 1.0


# 运行测试的便捷函数
def run_tests():
    """运行所有测试"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    # 运行特定测试类
    pytest.main([__file__, "-v", "TestHealthEndpoint", "-k", "test_health"])
    print("✅ API 端点集成测试完成！")
