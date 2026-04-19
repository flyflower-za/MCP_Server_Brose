#!/usr/bin/env python3
"""
创建新的MCP服务器模板
"""
import os
import sys
from pathlib import Path


def create_mcp_server(server_name: str, description: str = ""):
    """
    创建新的MCP服务器

    Args:
        server_name: 服务器名称（将用作目录名和模块名）
        description: 服务描述
    """
    # 规范化服务器名称
    server_id = server_name.lower().replace(" ", "_").replace("-", "_")
    display_name = server_name.replace("_", " ").title()

    if not description:
        description = f"{display_name}服务"

    # 创建服务器目录
    server_dir = Path("mcp_servers") / server_id
    server_dir.mkdir(parents=True, exist_ok=True)

    # 创建__init__.py
    init_content = f'"""
{display_name}模块
"""
from .server import router, get_info

__all__ = ["router", "get_info"]
'
    (server_dir / "__init__.py").write_text(init_content)

    # 创建models.py
    models_content = f'"""
{display_name}的数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class ProcessRequest(BaseModel):
    """处理请求"""
    input_data: str = Field(..., description="输入数据")
    param1: Optional[str] = Field(default="", description="可选参数1")


class ProcessResponse(BaseModel):
    """处理响应"""
    success: bool
    result: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
'
    (server_dir / "models.py").write_text(models_content)

    # 创建server.py
    server_content = f'"""
{display_name} MCP服务器
"""
from fastapi import APIRouter
from .models import ProcessRequest, ProcessResponse
from utils.logger import logger


# 创建路由器
router = APIRouter(prefix="/{server_id}", tags=["{display_name}"])


@router.post("/process", response_model=ProcessResponse)
async def process(request: ProcessRequest):
    """
    处理请求的主要端点

    Args:
        request: 处理请求对象

    Returns:
        处理结果
    """
    try:
        logger.info(f"处理请求: {{request.input_data}}")

        # 在这里实现你的业务逻辑
        result = f"处理完成: {{request.input_data}}"

        return ProcessResponse(
            success=True,
            result=result,
            message="处理成功"
        )

    except Exception as e:
        logger.error(f"处理失败: {{str(e)}}")
        return ProcessResponse(
            success=False,
            error=f"处理失败: {{str(e)}}"
        )


@router.get("/info")
async def get_info_endpoint():
    """获取服务信息"""
    return get_info()


def get_info():
    """获取服务器信息"""
    return {{
        "name": "{display_name}",
        "version": "1.0.0",
        "description": "{description}",
        "endpoints": [
            {{"path": "/{server_id}/process", "method": "POST", "description": "处理请求"}},
            {{"path": "/{server_id}/info", "method": "GET", "description": "获取服务信息"}}
        ]
    }}
'
    (server_dir / "server.py").write_text(server_content)

    # 更新settings.py
    settings_path = Path("config/settings.py")
    if settings_path.exists():
        settings_content = settings_path.read_text()

        # 查找MCP_SERVERS_CONFIG的位置
        import_index = settings_content.find("MCP_SERVERS_CONFIG")
        if import_index == -1:
            print("⚠️  无法在config/settings.py中找到MCP_SERVERS_CONFIG")
            print(f"请手动添加以下配置到MCP_SERVERS_CONFIG字典中:")
            print(f"""
    "{server_id}": {{
        "name": "{display_name}",
        "description": "{description}",
        "enabled": True,
        "version": "1.0.0",
        "module": "mcp_servers.{server_id}.server",
        "prefix": "/{server_id}",
        "tags": ["{server_id}"]
    }},""")
        else:
            # 找到字典的结束位置
            dict_start = settings_content.find("{", import_index)
            dict_end = settings_content.rfind("}", import_index) + 1

            # 在字典末尾添加新配置
            new_config = f"""
    "{server_id}": {{
        "name": "{display_name}",
        "description": "{description}",
        "enabled": True,
        "version": "1.0.0",
        "module": "mcp_servers.{server_id}.server",
        "prefix": "/{server_id}",
        "tags": ["{server_id}"]
    }},"""

            # 插入新配置
            updated_settings = (
                settings_content[:dict_end - 1] +
                new_config +
                settings_content[dict_end - 1:]
            )

            settings_path.write_text(updated_settings)
            print(f"✅ 已更新config/settings.py")

    print(f"\n{'='*60}")
    print(f"✅ MCP服务器 '{display_name}' 创建完成！")
    print(f"{'='*60}")
    print(f"\n📁 创建的文件:")
    print(f"   - {server_dir}/__init__.py")
    print(f"   - {server_dir}/models.py")
    print(f"   - {server_dir}/server.py")
    print(f"\n📝 下一步:")
    print(f"   1. 编辑 {server_dir}/server.py 实现你的业务逻辑")
    print(f"   2. 编辑 {server_dir}/models.py 定义数据模型")
    print(f"   3. 重启服务器: python main.py")
    print(f"\n📍 API端点将注册为: /{server_id}")
    print(f"{'='*60}\n")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python create_mcp_server.py <服务器名称> [描述]")
        print("示例: python create_mcp_server.py image_processor '图片处理服务'")
        sys.exit(1)

    server_name = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else ""

    create_mcp_server(server_name, description)


if __name__ == "__main__":
    main()
