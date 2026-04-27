# 二维码识别器 MCP Server 使用文档

## 概述

二维码识别器 MCP Server 提供了从图片中提取二维码内容的功能。支持多种输入方式，包括图片URL、Base64编码的图片数据，以及文本形式输入。

## 功能特性

- ✅ **图片URL识别**：支持通过URL下载并识别图片中的二维码
- ✅ **Base64识别**：支持Base64编码的图片数据识别
- ✅ **文本输入**：支持直接处理文本形式的二维码内容
- ✅ **批量处理**：支持一次性识别多个二维码
- ✅ **位置信息**：返回二维码在图片中的位置坐标
- ✅ **错误处理**：完善的错误处理和日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `opencv-python>=4.8.0` - 计算机视觉库，用于二维码检测
- `Pillow>=10.0.0` - 图像处理库
- `qrcode>=7.4.0` - 二维码生成和识别库

## API 端点

### 1. 识别单个二维码

**端点**: `POST /qrcode/read`

**请求体**:
```json
{
  "image_url": "https://example.com/qrcode.png",
  "image_base64": "base64编码的图片数据",
  "text_input": "文本形式的二维码内容"
}
```

**参数说明**:
- `image_url` (可选): 图片的URL地址
- `image_base64` (可选): Base64编码的图片数据
- `text_input` (可选): 文本形式的二维码内容

**响应**:
```json
{
  "success": true,
  "qr_data": "二维码内容",
  "format": "QR_CODE",
  "error": null,
  "metadata": {
    "type": "QR_CODE",
    "bbox": [[[50.0, 50.0], [299.0, 50.0], [299.0, 299.0], [50.0, 299.0]]],
    "detected": true
  }
}
```

### 2. 批量识别二维码

**端点**: `POST /qrcode/read/batch`

**请求体**:
```json
{
  "requests": [
    {
      "image_url": "https://example.com/qrcode1.png"
    },
    {
      "image_base64": "base64编码的图片数据"
    }
  ]
}
```

**响应**:
```json
{
  "results": [
    {
      "success": true,
      "qr_data": "第一个二维码内容",
      "format": "QR_CODE",
      "error": null,
      "metadata": {...}
    },
    {
      "success": true,
      "qr_data": "第二个二维码内容",
      "format": "QR_CODE",
      "error": null,
      "metadata": {...}
    }
  ],
  "total_success": 2,
  "total_failed": 0
}
```

### 3. 健康检查

**端点**: `GET /qrcode/health`

**响应**:
```json
{
  "status": "healthy",
  "service": "QR Code Reader",
  "version": "1.0.0"
}
```

## 使用示例

### Python 客户端示例

```python
import requests
import base64

# 示例1: 从URL识别二维码
response = requests.post("http://localhost:8000/qrcode/read", json={
    "image_url": "https://example.com/qrcode.png"
})
result = response.json()
print(result["qr_data"])

# 示例2: 从Base64识别二维码
with open("qrcode.png", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode()

response = requests.post("http://localhost:8000/qrcode/read", json={
    "image_base64": img_base64
})
result = response.json()
print(result["qr_data"])

# 示例3: 批量识别
response = requests.post("http://localhost:8000/qrcode/read/batch", json={
    "requests": [
        {"image_url": "https://example.com/qrcode1.png"},
        {"image_url": "https://example.com/qrcode2.png"}
    ]
})
results = response.json()
for result in results["results"]:
    print(f"成功: {result['success']}, 数据: {result.get('qr_data')}")
```

### cURL 示例

```bash
# 从URL识别二维码
curl -X POST http://localhost:8000/qrcode/read \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/qrcode.png"}'

# 从Base64识别二维码
curl -X POST http://localhost:8000/qrcode/read \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}'

# 健康检查
curl http://localhost:8000/qrcode/health
```

## 配置

二维码识别器在 `config/settings.py` 中配置：

```python
"qrcode_reader": {
    "name": "QR Code Reader",
    "description": "Extract content from QR codes in images",
    "enabled": True,
    "version": "1.0.0",
    "module": "mcp_servers.qrcode_reader.server",
    "prefix": "/qrcode",
    "tags": ["qrcode", "image", "reader", "barcode"]
}
```

## 测试

运行测试脚本：

```bash
# 基础测试
python test_qrcode.py

# 完整测试（包含真实二维码）
python test_qrcode_complete.py
```

## 技术实现

- **图像处理**: OpenCV (cv2)
- **二维码检测**: cv2.QRCodeDetector
- **图像格式**: PIL/Pillow
- **Web框架**: FastAPI
- **进程管理**: 独立进程运行

## 错误处理

系统会处理以下错误情况：
- ❌ 无效的图片URL
- ❌ 无效的Base64数据
- ❌ 图片中未检测到二维码
- ❌ 图片格式不支持
- ❌ 缺少必要参数

每个错误都会返回详细的错误信息，方便调试。

## 性能优化

- 使用OpenCV的原生二维码检测器，性能优异
- 支持批量处理，减少网络开销
- 独立进程运行，不影响其他服务
- 完善的日志记录，便于监控

## 未来改进

- [ ] 支持条形码识别
- [ ] 支持多个二维码同时识别
- [ ] 添加二维码生成功能
- [ ] 支持更多图片格式
- [ ] 添加图片预处理选项（去噪、旋转等）

## 许可证

MIT License
