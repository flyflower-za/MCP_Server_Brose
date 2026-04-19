#!/usr/bin/env python3
"""
MCP服务器管理系统客户端示例
"""
import requests
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 统一读取配置
MCP_PORT = os.getenv("MCP_PORT", "51234")
MCP_HOST = os.getenv("MCP_HOST", "localhost")

# 客户端无法连接到 0.0.0.0，需要转换为 localhost
CLIENT_HOST = "localhost" if MCP_HOST == "0.0.0.0" else MCP_HOST
MCP_BASE_URL = f"http://{CLIENT_HOST}:{MCP_PORT}"


class MCPHubClient:
    """MCP服务器管理系统客户端"""

    def __init__(self, base_url=None):
        self.base_url = base_url or MCP_BASE_URL
        self.server_ports = {}  # 缓存服务器端口

    def _get_server_port(self, server_id):
        """获取服务器端口"""
        if server_id not in self.server_ports:
            response = requests.get(f"{self.base_url}/api/v1/servers/{server_id}/status")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "running":
                    self.server_ports[server_id] = data["port"]
                    return data["port"]
        return self.server_ports.get(server_id)

    def get_system_info(self):
        """获取系统信息"""
        response = requests.get(f"{self.base_url}/")
        return response.json()

    def health_check(self):
        """健康检查"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def list_servers(self):
        """列出所有服务器"""
        response = requests.get(f"{self.base_url}/api/v1/servers")
        return response.json()

    def extract_pdf(self, url, include_metadata=True):
        """提取PDF"""
        port = self._get_server_port("pdf_extractor")
        if not port:
            raise Exception("PDF提取器服务器未运行")

        response = requests.post(
            f"http://localhost:{port}/extract",
            json={
                "url": url,
                "include_metadata": include_metadata
            }
        )
        response.raise_for_status()
        return response.json()

    def extract_batch_pdfs(self, urls, include_metadata=True):
        """批量提取PDF"""
        port = self._get_server_port("pdf_extractor")
        if not port:
            raise Exception("PDF提取器服务器未运行")

        response = requests.post(
            f"http://localhost:{port}/extract/batch",
            json={
                "urls": urls,
                "include_metadata": include_metadata
            }
        )
        response.raise_for_status()
        return response.json()


def main():
    """交互式客户端"""
    client = MCPHubClient()

    print("=" * 60)
    print("MCP服务器管理系统 - 客户端")
    print("=" * 60)
    print(f"🔗 连接地址: {client.base_url}")
    print(f"📡 从 .env 文件读取配置 (MCP_PORT={os.getenv('MCP_PORT', '8000')}, MCP_HOST={os.getenv('MCP_HOST', 'localhost')})")

    # 检查连接
    try:
        health = client.health_check()
        print(f"\n✅ 系统状态: {health['status']}")
        print(f"📊 已加载服务器: {health['loaded_servers']}个")
    except Exception as e:
        print(f"\n❌ 无法连接到服务器: {str(e)}")
        print("请确保服务器已启动: python main.py")
        return

    # 显示系统信息
    print("\n" + "=" * 60)
    print("系统信息")
    print("=" * 60)

    system_info = client.get_system_info()
    print(f"\n系统: {system_info['system']}")
    print(f"版本: {system_info['version']}")
    print(f"API前缀: {system_info['api_prefix']}")

    # 显示服务器列表
    print("\n" + "=" * 60)
    print("可用的MCP服务器")
    print("=" * 60)

    servers = client.list_servers()
    for i, server in enumerate(servers['servers'], 1):
        print(f"\n{i}. {server['name']} ({server['id']})")
        print(f"   描述: {server['description']}")
        print(f"   版本: {server['version']}")
        print(f"   前缀: {server['prefix']}")
        print(f"   状态: {server['runtime_status']['status']}")
        print(f"   进程: {server['runtime_status']['pid']}")

        # 显示端点信息（如果有的话）
        print(f"   端点:")
        print(f"     - POST /pdf/extract")
        print(f"     - POST /pdf/extract/batch")

    # PDF提取示例
    print("\n" + "=" * 60)
    print("PDF提取器测试")
    print("=" * 60)

    test_url = input("\n请输入PDF URL (直接回车使用默认示例): ").strip()
    if not test_url:
        test_url = "https://myctiapi.cti-soft.com:58443/api/HomeQuery/PreviewReportH5?ReportNo=A225097188910101C;198641334"

    print(f"\n📋 正在提取: {test_url}")

    try:
        result = client.extract_pdf(test_url)

        if result["success"]:
            print(f"\n✅ 提取成功!")
            print(f"   - 总页数: {result['total_pages']}")
            print(f"   - 字符数: {len(result['content'])}")

            if result.get('metadata'):
                print(f"\n📋 元数据:")
                for key, value in result['metadata'].items():
                    if value:
                        print(f"   - {key}: {value}")

            # 保存到文件
            output_file = "extracted_content.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"URL: {result['url']}\n")
                f.write(f"总页数: {result['total_pages']}\n")
                if result.get('metadata'):
                    f.write(f"\n元数据:\n")
                    for key, value in result['metadata'].items():
                        if value:
                            f.write(f"  {key}: {value}\n")
                f.write(f"\n内容:\n")
                f.write(result['content'])

            print(f"\n💾 内容已保存到: {output_file}")

        else:
            print(f"\n❌ 提取失败: {result['error']}")

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
