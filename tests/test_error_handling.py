"""
测试统一错误处理系统
"""
import json
from utils.error_handlers import (
    APIError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    create_error_response
)


def test_error_response_format():
    """测试错误响应格式"""
    response = create_error_response(
        status_code=404,
        message="资源未找到",
        error_code="NOT_FOUND",
        details={"resource_id": "123"}
    )

    assert response.status_code == 404
    content = response.body.decode()
    data = json.loads(content)

    assert data["success"] is False
    assert data["error"]["code"] == "NOT_FOUND"
    assert data["error"]["message"] == "资源未找到"
    assert data["error"]["details"]["resource_id"] == "123"


def test_custom_errors():
    """测试自定义错误类"""
    # NotFoundError
    error = NotFoundError(
        message="服务器不存在",
        details={"server_id": "test_server"}
    )
    assert error.status_code == 404
    assert error.error_code == "NOT_FOUND"
    assert error.message == "服务器不存在"

    # ValidationError
    error = ValidationError(
        message="参数验证失败",
        details={"field": "port", "value": "invalid"}
    )
    assert error.status_code == 422
    assert error.error_code == "VALIDATION_ERROR"

    # AuthenticationError
    error = AuthenticationError(
        message="密码错误"
    )
    assert error.status_code == 401
    assert error.error_code == "AUTHENTICATION_ERROR"


def test_error_inheritance():
    """测试错误继承关系"""
    error = APIError(
        message="基础错误",
        status_code=500,
        error_code="BASE_ERROR"
    )

    assert isinstance(error, Exception)
    assert str(error) == "基础错误"


def test_error_details():
    """测试错误详情处理"""
    details = {
        "server_id": "pdf_extractor",
        "port": 51235,
        "error": "Address already in use"
    }

    error = APIError(
        message="启动失败",
        details=details
    )

    assert error.details == details
    assert error.details["server_id"] == "pdf_extractor"


def test_error_codes():
    """测试错误代码常量"""
    assert NotFoundError("test").error_code == "NOT_FOUND"
    assert ValidationError("test").error_code == "VALIDATION_ERROR"
    assert AuthenticationError("test").error_code == "AUTHENTICATION_ERROR"

    # 测试自定义错误代码
    error = APIError(
        message="自定义错误",
        error_code="CUSTOM_ERROR"
    )
    assert error.error_code == "CUSTOM_ERROR"


if __name__ == "__main__":
    # 运行测试
    test_error_response_format()
    test_custom_errors()
    test_error_inheritance()
    test_error_details()
    test_error_codes()
    print("✅ 所有错误处理测试通过！")
