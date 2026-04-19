# 🔌 n8n调用MCP服务器完整指南

## 🚀 快速开始

### 1️⃣ 确认MCP服务器配置

```bash
# 查看当前配置
cat .env

# 确认监听地址（重要！）
MCP_HOST=0.0.0.0  # 允许外部访问
MCP_PORT=51234    # 你的端口号
```

### 2️⃣ 获取访问地址

```bash
# 方法A: 使用localhost (仅本地)
http://localhost:51234

# 方法B: 使用本地IP (同一网络)
http://192.168.x.x:51234

# 方法C: 使用0.0.0.0 (所有接口)
http://0.0.0.0:51234
```

---

## 🎯 n8n工作流配置

### **基础HTTP Request节点配置**

#### **节点1: PDF提取请求**

**节点类型:** `HTTP Request`

**配置:**
```json
{
  "method": "POST",
  "url": "http://localhost:51234/extract",
  "authentication": "none",
  "requestBody": {
    "contentType": "application/json",
    "body": {
      "url": "={{$json.pdf_url}}",
      "include_metadata": true
    }
  }
}
```

**字段说明:**
- `url`: 你的PDF文件URL
- `include_metadata`: 是否包含元数据 (true/false)

---

### **完整n8n工作流示例**

#### **工作流1: 简单PDF提取**

```
节点1: Manual Trigger (手动触发)
  ↓
节点2: HTTP Request (提取PDF)
  - Method: POST
  - URL: http://localhost:51234/extract
  - Body: {
    "url": "你的PDF_URL",
    "include_metadata": true
  }
  ↓
节点3: Set (处理结果)
  - 提取文本内容
```

#### **工作流2: 批量PDF处理**

```
节点1: Manual Trigger
  ↓
节点2: Code (准备PDF URL列表)
  - 返回多个PDF URL
  ↓
节点3: Loop Over Items (循环处理)
  ↓
节点4: HTTP Request (提取每个PDF)
  - URL: http://localhost:51234/extract
  ↓
节点5: Aggregate (聚合结果)
```

---

## 🔧 n8n详细配置步骤

### **步骤1: 创建HTTP Request节点**

1. 拖拽 `HTTP Request` 节点到画布
2. 配置节点：
   - **Method**: `POST`
   - **URL**: `http://localhost:51234/extract`
   - **Authentication**: `None`
   - **Content Type**: `JSON`

### **步骤2: 配置请求体**

在 `Body Parameters` 中添加：

```json
{
  "url": "https://example.com/your-file.pdf",
  "include_metadata": true
}
```

### **步骤3: 测试连接**

点击 `Test Step` 按钮测试节点：
```bash
# 预期响应：
{
  "success": true,
  "url": "https://example.com/your-file.pdf",
  "total_pages": 5,
  "content": "提取的文本内容...",
  "metadata": {...}
}
```

---

## 🌐 网络配置

### **本地访问 (localhost)**

```json
{
  "url": "http://localhost:51234/extract"
}
```

### **局域网访问 (推荐)**

```bash
# 1. 获取你的本地IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# 2. 在n8n中使用本地IP
{
  "url": "http://192.168.1.100:51234/extract"
}
```

### **确保服务器允许外部访问**

检查 `.env` 配置：
```bash
MCP_HOST=0.0.0.0  # 必须！允许外部访问
MCP_PORT=51234
```

---

## 🎯 实际n8n工作流JSON

### **简单PDF提取工作流**

```json
{
  "name": "PDF Extractor",
  "nodes": [
    {
      "type": "n8n-nodes-base.manualTrigger",
      "name": "Manual Trigger",
      "position": [250, 300]
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Extract PDF",
      "position": [450, 300],
      "parameters": {
        "method": "POST",
        "url": "http://localhost:51234/extract",
        "authentication": "none",
        "requestBody": {
          "contentType": "application/json",
          "body": {
            "url": "https://myctiapi.cti-soft.com:58443/api/HomeQuery/PreviewReportH5?ReportNo=A225097188910101C;198641334",
            "include_metadata": true
          }
        }
      }
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [
        [
          {
            "node": "Extract PDF",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## 🔍 API端点详解

### **可用端点**

| 端点 | 方法 | 功能 | n8n节点类型 |
|------|------|------|------------|
| `/extract` | POST | 提取单个PDF | HTTP Request |
| `/extract/batch` | POST | 批量提取PDF | HTTP Request |
| `/health` | GET | 健康检查 | HTTP Request |
| `/` | GET | 系统信息 | HTTP Request |

### **请求/响应格式**

#### **单个PDF提取**
```json
// 请求
{
  "url": "PDF文件URL",
  "include_metadata": true
}

// 响应
{
  "success": true,
  "url": "PDF文件URL",
  "total_pages": 5,
  "content": "提取的文本内容",
  "metadata": {
    "title": "文档标题",
    "author": "作者",
    "creator": "创建工具",
    "producer": "生成工具"
  }
}
```

#### **批量PDF提取**
```json
// 请求
{
  "urls": ["URL1", "URL2", "URL3"],
  "include_metadata": true
}

// 响应
{
  "results": [...],
  "total_success": 3,
  "total_failed": 0
}
```

---

## 🛠️ 故障排除

### **问题1: 连接被拒绝**

```bash
# 检查服务器是否运行
curl http://localhost:51234/health

# 检查防火墙
# 确保端口51234未被阻止
```

### **问题2: 超时错误**

```bash
# 在.env中增加超时时间
REQUEST_TIMEOUT=60

# 重启服务器
```

### **问题3: 无法从局域网访问**

```bash
# 1. 确认MCP_HOST=0.0.0.0
grep "MCP_HOST" .env

# 2. 检查防火墙设置
# macOS: 系统偏好设置 -> 安全性与隐私 -> 防火墙

# 3. 使用本地IP而非localhost
# 在n8n中使用: http://192.168.x.x:51234
```

---

## 🎯 n8n高级用法

### **动态URL处理**

使用n8n表达式动态设置PDF URL：

```json
{
  "url": "={{$json.pdf_url}}"
}
```

### **条件处理**

根据提取结果执行不同操作：

```javascript
// 在Code节点中
const extractionResult = items[0].json;

if (extractionResult.success) {
  return [{
    json: {
      status: "success",
      pages: extractionResult.total_pages,
      content: extractionResult.content
    }
  }];
} else {
  return [{
    json: {
      status: "failed",
      error: extractionResult.error
    }
  }];
}
```

### **批量处理**

使用n8n的Loop节点处理多个PDF：

```
1. Code节点: 生成URL列表
2. Loop Over Items: 遍历每个URL  
3. HTTP Request: 调用/extract端点
4. Aggregate: 聚合所有结果
```

---

## 📝 最佳实践

### **1. 错误处理**

在n8n工作流中添加错误处理节点：
```javascript
// 检查API响应
if (!$json.success) {
  throw new Error($json.error || "PDF提取失败");
}
```

### **2. 超时设置**

对于大文件，设置合理的超时：
```bash
# 在.env中
REQUEST_TIMEOUT=120
```

### **3. 重试机制**

在HTTP Request节点中启用重试：
- 最大重试次数: 3
- 重试延迟: 1000ms

---

## 🚀 快速测试

### **方法1: 使用curl测试**

```bash
curl -X POST "http://localhost:51234/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://myctiapi.cti-soft.com:58443/api/HomeQuery/PreviewReportH5?ReportNo=A225097188910101C;198641334",
    "include_metadata": true
  }'
```

### **方法2: 在n8n中测试**

1. 创建HTTP Request节点
2. 使用上述配置
3. 点击 "Test Step"
4. 查看响应结果

---

## 💡 总结

**n8n调用MCP服务器的关键点:**

1. **🌐 URL配置** - 使用正确的服务器地址
2. **📋 端点选择** - 根据需要选择/extract或/extract/batch
3. **🔧 参数配置** - 正确设置url和include_metadata
4. **⚠️ 网络配置** - 确保MCP_HOST=0.0.0.0允许外部访问

**开始使用:**
1. 确认MCP服务器运行正常
2. 在n8n中创建HTTP Request节点
3. 使用上述配置连接到你的服务器
4. 测试PDF提取功能

**🎯 现在可以在n8n中工作流化PDF处理了！**
