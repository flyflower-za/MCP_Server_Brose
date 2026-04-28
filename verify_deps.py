#!/usr/bin/env python3
"""MCP Server Hub 依赖验证脚本"""
import sys

def check_module(module_name, display_name=None):
    """检查模块是否可导入"""
    if display_name is None:
        display_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {display_name}")
        return True
    except ImportError as e:
        print(f"❌ {display_name} - {str(e)[:50]}")
        return False

def main():
    """主检查函数"""
    print("🔍 检查 MCP Server Hub 依赖...\n")
    
    dependencies = [
        # 核心框架
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("starlette", "Starlette"),
        
        # HTTP 客户端
        ("requests", "Requests"),
        ("httpx", "HTTPX"),
        
        # 文档处理
        ("PyPDF2", "PyPDF2"),
        ("endesive", "Endesive"),
        ("cryptography", "Cryptography"),
        
        # 图像处理
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("qrcode", "QRCode"),
        
        # 系统工具
        ("psutil", "psutil"),
        ("dotenv", "python-dotenv"),
        
        # 安全认证
        ("jwt", "PyJWT"),
        ("bcrypt", "bcrypt"),
    ]
    
    passed = 0
    failed = 0
    
    for module, display in dependencies:
        if check_module(module, display):
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 结果: {passed} 通过, {failed} 失败")
    
    if failed > 0:
        print("\n🔧 安装缺失依赖:")
        print("   pip install -r requirements.txt")
        print("\n📚 查看详细指南:")
        print("   cat docs/DEPENDENCY_INSTALLATION_GUIDE.md")
        return 1
    else:
        print("\n✅ 所有依赖已正确安装！")
        print("🚀 启动服务: python3 main.py")
        return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⚠️  检查被中断")
        sys.exit(130)
