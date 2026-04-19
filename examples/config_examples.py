"""
MCP服务器配置示例
演示如何使用MCP服务器客户端
"""
import requests
import json


class MCPHubClient:
    """MCP服务器管理系统客户端示例"""

    def __init__(self, base_url="http://localhost:51234"):
        self.base_url = base_url

    def get_system_info(self):
        """获取系统信息"""
        try:
            response = requests.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def health_check(self):
        """健康检查"""
        try:
            response = requests.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def extract_pdf(self, url, include_metadata=True):
        """提取PDF内容"""
        try:
            response = requests.post(
                f"{self.base_url}/extract",
                json={
                    "url": url,
                    "include_metadata": include_metadata
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def extract_batch_pdfs(self, urls, include_metadata=True):
        """批量提取PDF"""
        try:
            response = requests.post(
                f"{self.base_url}/extract/batch",
                json={
                    "urls": urls,
                    "include_metadata": include_metadata
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def main():
    """使用示例"""
    client = MCPHubClient()

    print("=" * 60)
    print("MCP服务器配置示例")
    print("=" * 60)

    # 1. 健康检查
    print("\n1. Health Check:")
    health = client.health_check()
    if "error" not in health:
        print(f"Server Status: {health['status']}")
    else:
        print(f"Connection Failed: {health['error']}")
        return

    # 2. 系统信息
    print("\n2. System Info:")
    info = client.get_system_info()
    if "error" not in info:
        print(f"System: {info['system']}")
        print(f"Version: {info['version']}")
        print(f"Loaded Servers: {info['loaded_servers']}")
    else:
        print(f"Failed to get info: {info['error']}")

    # 3. PDF提取示例
    print("\n3. PDF Extraction Example:")
    test_url = "https://myctiapi.cti-soft.com:58443/api/HomeQuery/PreviewReportH5?ReportNo=A225097188910101C;198641334"

    result = client.extract_pdf(test_url)
    if result.get("success"):
        print(f"Extraction Successful!")
        print(f"   Total Pages: {result['total_pages']}")
        print(f"   Character Count: {len(result['content'])}")
        if result.get('metadata'):
            print(f"   Author: {result['metadata'].get('author', 'N/A')}")
    else:
        print(f"Extraction Failed: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 60)
    print("Usage Tips:")
    print("  1. Ensure server is running: ./start_safe.sh")
    print("  2. Modify port configuration: Edit .env file")
    print("  3. View API docs: http://localhost:51234/docs")
    print("=" * 60)


if __name__ == "__main__":
    main()
