#!/usr/bin/env python3
"""
快速测试脚本 - 模拟n8n调用
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:51234"
PDF_URL = "https://myctiapi.cti-soft.com:58443/api/HomeQuery/PreviewReportH5?ReportNo=A225097188910101C;198641334"

def test_n8n_style_call():
    """模拟n8n的HTTP Request节点调用"""
    print("🧪 模拟n8n HTTP Request节点调用")
    print("=" * 50)

    # 模拟n8n的HTTP Request配置
    n8n_config = {
        "method": "POST",
        "url": f"{BASE_URL}/extract",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": {
            "url": PDF_URL,
            "include_metadata": True
        }
    }

    print("📋 n8n节点配置:")
    print(json.dumps(n8n_config, indent=2))
    print("\n" + "=" * 50)

    try:
        # 执行HTTP请求（模拟n8n行为）
        response = requests.post(
            n8n_config["url"],
            headers=n8n_config["headers"],
            json=n8n_config["body"],
            timeout=30
        )

        # 处理响应
        if response.status_code == 200:
            result = response.json()

            print("✅ n8n节点执行成功!")
            print("\n📊 处理结果:")
            print(f"   - 成功: {result['success']}")
            print(f"   - 页数: {result['total_pages']}")
            print(f"   - 内容长度: {len(result['content'])}")

            if result.get('metadata'):
                print(f"\n📋 元数据:")
                for key, value in result['metadata'].items():
                    if value:
                        print(f"   - {key}: {value}")

            print(f"\n📝 内容预览 (前200字符):")
            print("-" * 50)
            print(result['content'][:200])
            if len(result['content']) > 200:
                print("...")
            print("-" * 50)

        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应: {response.text}")

    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

    print("\n" + "=" * 50)
    print("💡 n8n集成提示:")
    print("1. 在n8n中创建HTTP Request节点")
    print("2. 使用上述配置")
    print("3. URL字段可以使用n8n表达式: {{$json.pdf_url}}")
    print("4. 测试节点验证连接")

if __name__ == "__main__":
    test_n8n_style_call()
