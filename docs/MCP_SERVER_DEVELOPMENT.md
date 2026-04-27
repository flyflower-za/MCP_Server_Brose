# 🔧 MCP Server 模块开发完全指南

本文档详细说明如何创建、注册和集成新的 MCP Server 模块到 MCP Servers Hub 系统中。

## 📋 目录

- [概述](#概述)
- [准备工作](#准备工作)
- [创建模块结构](#创建模块结构)
- [实现服务逻辑](#实现服务逻辑)
- [注册到系统](#注册到系统)
- [Dashboard 集成](#dashboard-集成)
- [测试和调试](#测试和调试)
- [完整示例](#完整示例)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 🎯 概述

### MCP Server 模块是什么？

MCP Server 模块是一个独立的服务单元，运行在独立的进程中，通过 HTTP API 提供特定功能。系统采用进程隔离架构，每个模块都有自己的端口和资源。

### 模块特点

- 🔄 **进程隔离**: 每个模块运行在独立进程中
- 🌐 **HTTP API**: 通过 RESTful API 提供服务
- 🔌 **热插拔**: 支持动态启动/停止
- 📊 **可监控**: Dashboard 实时监控状态
- 🔧 **易扩展**: 标准化的模块结构

---

## 🛠️ 准备工作

### 1. 开发环境设置

#### 确保项目运行正常
```bash
# 检查系统状态
curl http://localhost:51234/health

# 预期响应
{
  "status": "healthy",
  "architecture": "process_isolation",
  "loaded_servers": 2,
  "running_servers": 2
}
```

#### 激活虚拟环境
```bash
# 确保在虚拟环境中
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows

# 验证环境
which python
# 应该显示: /path/to/.venv/bin/python
```

### 2. 规划你的模块

#### 确定模块功能
- **功能描述**: 模块提供什么服务？
- **输入输出**: API 接口的数据格式
- **依赖库**: 需要哪些 Python 库
- **资源需求**: CPU、内存、存储需求

#### 命名规范
```python
# 模块 ID (小写，下划线分隔)
server_id = "my_service"

# 模块名称 (首字母大写，空格分隔)
name = "My Service"

# URL 前缀 (小写，斜杠包围)
prefix = "/my_service"
```

---

## 📂 创建模块结构

### 标准模块目录结构

```bash
mcp_servers/
└── my_service/              # 你的模块目录
    ├── __init__.py          # 模块初始化文件
    ├── server.py            # 服务实现和路由定义
    └── models.py            # 数据模型定义
```

### 1. 创建目录

```bash
# 在项目根目录执行
mkdir -p mcp_servers/my_service
cd mcp_servers/my_service
```

### 2. 创建 `__init__.py`

这个文件导出模块的核心组件，让系统能够发现和加载你的服务。

```python
"""
My Service MCP 服务器
"""
from mcp_servers.my_service.server import router, get_info

__all__ = ['router', 'get_info']
```

**关键点**:
- 必须导出 `router` (FastAPI 路由器)
- 必须导出 `get_info` (返回服务信息的函数)

### 3. 创建 `models.py`

定义 API 的数据模型，使用 Pydantic 进行数据验证。

```python
"""
My Service 的数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class MyServiceRequest(BaseModel):
    """My Service 请求模型"""
    input_data: str = Field(..., description="输入数据")
    option_flag: bool = Field(default=False, description="可选标志")
    count: int = Field(default=1, ge=1, le=100, description="计数")

    class Config:
        json_schema_extra = {
            "example": {
                "input_data": "example data",
                "option_flag": True,
                "count": 5
            }
        }


class MyServiceResponse(BaseModel):
    """My Service 响应模型"""
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None


class BatchMyServiceRequest(BaseModel):
    """批量处理请求模型"""
    requests: List[MyServiceRequest] = Field(..., description="请求列表")


class BatchMyServiceResponse(BaseModel):
    """批量处理响应模型"""
    results: List[MyServiceResponse]
    total_success: int
    total_failed: int
```

**关键点**:
- 使用 `Field` 添加描述和验证规则
- 提供默认值和示例
- 定义清晰的输入/输出模型
- 支持批量操作（可选）

---

## 💻 实现服务逻辑

### 创建 `server.py`

这是核心实现文件，定义 API 端点和业务逻辑。

```python
"""
My Service MCP 服务器
"""
from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

# 导入数据模型
from mcp_servers.my_service.models import (
    MyServiceRequest,
    MyServiceResponse,
    BatchMyServiceRequest,
    BatchMyServiceResponse
)

# 导入工具函数
from utils.logger import logger

# 创建路由器
router = APIRouter(tags=["My Service"])


def process_my_service_logic(request: MyServiceRequest) -> Dict[str, Any]:
    """
    核心业务逻辑实现
    
    Args:
        request: 请求数据
        
    Returns:
        处理结果字典
    """
    try:
        logger.info(f"处理 My Service 请求: {request.input_data}")
        
        # 你的业务逻辑在这里
        result_data = f"Processed: {request.input_data}"
        
        if request.option_flag:
            result_data += " [with flag]"
        
        if request.count > 1:
            result_data = f"{result_data}\n" * request.count
        
        return {
            "success": True,
            "result": result_data,
            "error": None,
            "metadata": {
                "input_length": len(request.input_data),
                "options": {
                    "flag": request.option_flag,
                    "count": request.count
                }
            }
        }
        
    except Exception as e:
        logger.error(f"My Service 处理失败: {str(e)}")
        return {
            "success": False,
            "result": None,
            "error": f"处理失败: {str(e)}",
            "metadata": None
        }


# ==================== API 端点 ====================

@router.post("/process", response_model=MyServiceResponse)
async def process_request(request: MyServiceRequest):
    """
    处理单个请求
    
    ## 功能说明
    - 接收输入数据并处理
    - 支持可选的标志和计数参数
    - 返回处理结果
    """
    result = process_my_service_logic(request)
    return MyServiceResponse(**result)


@router.post("/process/batch", response_model=BatchMyServiceResponse)
async def process_batch(request: BatchMyServiceRequest):
    """
    批量处理多个请求
    
    ## 功能说明
    - 接收多个请求并批量处理
    - 返回每个请求的处理结果
    - 统计成功和失败数量
    """
    results = []
    success_count = 0
    failed_count = 0
    
    for req in request.requests:
        result = process_my_service_logic(req)
        results.append(MyServiceResponse(**result))
        
        if result["success"]:
            success_count += 1
        else:
            failed_count += 1
    
    return BatchMyServiceResponse(
        results=results,
        total_success=success_count,
        total_failed=failed_count
    )


@router.get("/health")
async def health_check():
    """
    健康检查端点
    
    ## 返回服务状态
    - 用于监控服务是否正常运行
    - 系统会定期调用此端点
    """
    return {
        "status": "healthy",
        "service": "My Service",
        "version": "1.0.0"
    }


def get_info():
    """
    返回服务信息
    
    ## 系统调用时机
    - 启动时注册服务
    - Dashboard 显示服务信息
    - API 文档生成
    """
    return {
        "name": "My Service",
        "version": "1.0.0",
        "description": "我的自定义 MCP 服务",
        "endpoints": [
            {
                "path": "/my_service/process",
                "method": "POST",
                "description": "处理单个请求"
            },
            {
                "path": "/my_service/process/batch",
                "method": "POST",
                "description": "批量处理请求"
            },
            {
                "path": "/my_service/health",
                "method": "GET",
                "description": "健康检查"
            }
        ],
        "capabilities": [
            "支持单个请求处理",
            "支持批量处理",
            "可配置的选项参数",
            "详细的错误处理"
        ]
    }
```

**关键点**:
- 创建 `APIRouter` 实例
- 实现业务逻辑函数
- 定义 API 端点（使用装饰器）
- 实现 `get_info()` 函数返回服务信息
- 使用日志记录重要操作

---

## 📝 注册到系统

### 1. 更新 `config/settings.py`

在 `MCP_SERVERS_CONFIG` 字典中添加你的服务配置。

```python
# config/settings.py

MCP_SERVERS_CONFIG: Dict[str, Dict[str, Any]] = {
    "pdf_extractor": {
        "name": "PDF Extractor",
        "description": "Get PDF content from URLs",
        "enabled": True,
        "version": "1.0.0",
        "module": "mcp_servers.pdf_extractor.server",
        "prefix": "/pdf",
        "tags": ["pdf", "extractor", "document"]
    },
    "qrcode_reader": {
        "name": "QR Code Reader",
        "description": "Extract content from QR codes in images",
        "enabled": True,
        "version": "1.0.0",
        "module": "mcp_servers.qrcode_reader.server",
        "prefix": "/qrcode",
        "tags": ["qrcode", "image", "reader", "barcode"]
    },
    # 🆕 添加你的服务配置
    "my_service": {
        "name": "My Service",                    # 服务显示名称
        "description": "My custom MCP service",  # 服务描述
        "enabled": True,                         # 是否启用
        "version": "1.0.0",                      # 版本号
        "module": "mcp_servers.my_service.server", # Python 模块路径
        "prefix": "/my_service",                 # URL 前缀
        "tags": ["custom", "service", "demo"]     # 标签（用于分类）
    },
}
```

**配置字段说明**:
- **`name`**: 服务显示名称（Dashboard 中显示）
- **`description`**: 服务功能描述
- **`enabled`**: 是否启用服务（`True`/`False`）
- **`version`**: 服务版本号
- **`module`**: Python 模块路径（格式：`mcp_servers.{server_id}.server`）
- **`prefix`**: URL 路径前缀（格式：`/{server_id}`）
- **`tags`**: 服务标签列表（用于分类和搜索）

### 2. 更新依赖（如需要）

如果你的服务需要额外的 Python 库，更新 `requirements.txt`。

```bash
# requirements.txt

# 现有依赖...
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
# ...

# 🆕 添加你的服务依赖
# 例如：图像处理
Pillow>=10.0.0
opencv-python>=4.8.0

# 例如：数据处理
pandas>=2.0.0
numpy>=1.24.0
```

### 3. 安装新依赖

```bash
# 安装依赖
pip install -r requirements.txt

# 或只安装新增的依赖
pip install Pillow opencv-python
```

---

## 🎨 Dashboard 集成

### 1. 更新 API 端点显示

编辑 `dashboard/index.html`，在 `generateApiEndpoints` 函数中添加你的服务端点。

```javascript
// dashboard/index.html

function generateApiEndpoints(id, config, status, currentPort) {
  const isRunning = status?.status === 'running';
  const port = currentPort || status?.port || '—';
  const prefix = config?.prefix || '';
  const endpoints = [];

  // 获取当前页面的hostname和port
  const hostname = window.location.hostname;
  const baseUrl = port !== '—' ? `http://${hostname}:${port}` : `http://${hostname}:[端口]`;

  // ==================== 现有服务 ====================
  
  // PDF Extractor
  if (id === 'pdf_extractor' || prefix === '/pdf') {
    endpoints.push({
      method: 'POST',
      url: `${baseUrl}/extract`,
      active: isRunning
    });
    endpoints.push({
      method: 'POST',
      url: `${baseUrl}/extract/batch`,
      active: isRunning
    });
  }

  // QR Code Reader
  else if (id === 'qrcode_reader' || prefix === '/qrcode') {
    endpoints.push({
      method: 'POST',
      url: `${baseUrl}/read`,
      active: isRunning
    });
    endpoints.push({
      method: 'POST',
      url: `${baseUrl}/read/batch`,
      active: isRunning
    });
    endpoints.push({
      method: 'GET',
      url: `${baseUrl}/health`,
      active: isRunning
    });
  }

  // 🆕 添加你的服务端点
  else if (id === 'my_service' || prefix === '/my_service') {
    endpoints.push({
      method: 'POST',
      url: `${baseUrl}/process`,
      active: isRunning
    });
    endpoints.push({
      method: 'POST',
      url: `${baseUrl}/process/batch`,
      active: isRunning
    });
    endpoints.push({
      method: 'GET',
      url: `${baseUrl}/health`,
      active: isRunning
    });
  }

  // 通用服务器状态API (Hub API)
  endpoints.push({
    method: 'GET',
    url: `${HUB_BASE}/api/v1/servers/${id}/status`,
    active: true // Hub API始终可用
  });

  // 如果没有特定端点，显示通用提示
  if (endpoints.length === 0) {
    return `
      <div class="api-endpoint-item" style="justify-content:center;color:var(--text-muted);font-size:11px;">
        暂无特定API端点
      </div>
    `;
  }

  return endpoints.map(ep => `
    <div class="api-endpoint-item">
      <span class="api-method ${ep.method.toLowerCase()}">${ep.method}</span>
      <span class="api-url">${ep.url}</span>
      <span class="api-status-badge ${ep.active ? 'active' : 'inactive'}">
        ${ep.active ? '可用' : '离线'}
      </span>
      <button class="api-copy-btn" onclick="copyToClipboard('${ep.url}', this)" title="复制URL">
        📋
      </button>
    </div>
  `).join('');
}
```

### 2. 添加测试面板（可选）

如果需要在 Dashboard 中添加测试面板，在侧边栏添加新的面板。

```html
<!-- 在 dashboard/index.html 的 sidebar 部分添加 -->

<!-- MY SERVICE TESTER -->
<div class="panel" id="panel-my-service-tester">
  <div class="panel-header" onclick="togglePanel('panel-my-service-tester')">
    <div class="panel-title">
      <span>⚡</span> My Service 测试
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
      <span id="my-service-badge" style="font-size:10px;padding:3px 8px;border-radius:999px;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.2);color:var(--accent-red);">
        离线
      </span>
      <div class="panel-collapse-indicator" title="点击展开/折叠">▼</div>
    </div>
  </div>
  <div class="panel-body">
    <div class="input-group">
      <label class="input-label">输入数据</label>
      <input id="my-service-input" class="input-field" type="text" 
             placeholder="输入测试数据" />
    </div>
    <div class="checkbox-group">
      <input type="checkbox" id="my-service-flag" />
      <label for="my-service-flag">启用选项标志</label>
    </div>
    <div class="input-group">
      <label class="input-label">计数 (1-100)</label>
      <input id="my-service-count" class="input-field" type="number" 
             min="1" max="100" value="1" />
    </div>
    <button class="btn btn-primary" id="my-service-submit-btn" 
            style="width:100%;justify-content:center;" 
            onclick="submitMyService()">
      ⚡ 处理请求
    </button>
    <div id="my-service-result" class="result-box" style="margin-top:14px;"></div>
  </div>
</div>
```

### 3. 添加 JavaScript 测试函数

```javascript
// 在 dashboard/index.html 的 <script> 部分添加

// state 变量
let myServiceOnline = false;

// 更新状态徽章
function updateMyServiceBadge() {
  const b = document.getElementById('my-service-badge');
  if (!b) return;
  b.style.cssText = myServiceOnline
    ? 'font-size:10px;padding:3px 8px;border-radius:999px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);color:var(--accent-green)'
    : 'font-size:10px;padding:3px 8px;border-radius:999px;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.2);color:var(--accent-red)';
  b.textContent = myServiceOnline ? '在线' : '离线';
}

// 测试函数
async function submitMyService() {
  const input = document.getElementById('my-service-input').value.trim();
  const flag = document.getElementById('my-service-flag').checked;
  const count = parseInt(document.getElementById('my-service-count').value);
  const btn = document.getElementById('my-service-submit-btn');
  const res = document.getElementById('my-service-result');

  if (!input) {
    toast('请输入测试数据', 'warning');
    return;
  }

  const requestData = {
    input_data: input,
    option_flag: flag,
    count: count
  };

  btn.disabled = true;
  btn.innerHTML = '⚡ 处理中…';
  res.className = 'result-box visible';
  res.style.color = 'var(--text-muted)';
  res.textContent = '⏳ 正在处理请求…';
  addLog(`My Service 测试: ${input.slice(0,50)}...`, 'INFO');

  try {
    const d = await api('/my_service/process', 'POST', requestData);
    if (d.success) {
      res.className = 'result-box visible success';
      res.textContent = `✅ 处理成功\n\n结果:\n${d.result}`;
      addLog(`My Service 测试成功`, 'SUCCESS');
      toast('处理成功！', 'success');
    } else {
      res.className = 'result-box visible error';
      res.textContent = `❌ 处理失败\n\n${d.error}`;
      addLog(`My Service 测试失败: ${d.error}`, 'ERROR');
      toast('处理失败', 'error');
    }
  } catch(e) {
    res.className = 'result-box visible error';
    res.textContent = `❌ 请求失败: ${e.message}\n\n请确认 my_service 正在运行`;
    addLog(`My Service 请求失败: ${e.message}`, 'ERROR');
    toast(`请求失败: ${e.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '⚡ 处理请求';
  }
}
```

### 4. 更新状态检查

在 `renderServers()` 函数中添加状态更新逻辑。

```javascript
// 在 renderServers() 函数中添加
for (const [id, data] of Object.entries(servers)) {
  if (data.status?.status === 'running') running++;
  if (id === 'pdf_extractor') pdfOnline = data.status?.status === 'running';
  if (id === 'qrcode_reader') qrcodeOnline = data.status?.status === 'running';
  
  // 🆕 添加你的服务状态检查
  if (id === 'my_service') myServiceOnline = data.status?.status === 'running';
  // ...
}

// 更新状态徽章
updateStats(running, total);
updatePDFBadge();
updateQRCodeBadge();
updateMyServiceBadge(); // 🆕 添加状态更新
```

---

## 🧪 测试和调试

### 1. 启动服务

```bash
# 重启系统以加载新服务
./start_safe.sh

# 或使用 PM2
mcp-server restart
```

### 2. 验证服务加载

```bash
# 检查服务状态
curl http://localhost:51234/health | python -m json.tool

# 预期输出应包含你的服务
{
  "status": "healthy",
  "servers": [
    "pdf_extractor",
    "qrcode_reader",
    "my_service"  # 🎉 你的新服务
  ]
}
```

### 3. 测试 API 端点

```bash
# 测试健康检查
curl http://localhost:51234/my_service/health | python -m json.tool

# 测试处理端点
curl -X POST http://localhost:51234/my_service/process \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": "test data",
    "option_flag": true,
    "count": 3
  }' | python -m json.tool
```

### 4. Dashboard 测试

1. 访问 `http://localhost:51234/dashboard`
2. 找到你的服务卡片
3. 检查服务状态（应该是"运行中"）
4. 查看 API 端点显示
5. 使用测试面板测试功能

### 5. 查看日志

```bash
# 实时查看日志
tail -f logs/mcp_server.log

# 搜索你的服务日志
grep "my_service" logs/mcp_server.log

# 查看错误日志
grep "ERROR.*my_service" logs/mcp_server.log
```

---

## 📚 完整示例

### 示例：文本处理服务

这是一个完整的文本处理服务示例，包含大小写转换、统计信息等功能。

#### 1. 目录结构
```bash
mcp_servers/
└── text_processor/
    ├── __init__.py
    ├── server.py
    └── models.py
```

#### 2. `models.py`
```python
"""
文本处理器的数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class TextProcessRequest(BaseModel):
    """文本处理请求"""
    text: str = Field(..., description="要处理的文本")
    action: str = Field(..., description="操作类型: uppercase, lowercase, reverse")
    remove_spaces: bool = Field(default=False, description="移除空格")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello World",
                "action": "uppercase",
                "remove_spaces": False
            }
        }


class TextProcessResponse(BaseModel):
    """文本处理响应"""
    success: bool
    original: Optional[str] = None
    processed: Optional[str] = None
    stats: Optional[dict] = None
    error: Optional[str] = None
```

#### 3. `server.py`
```python
"""
文本处理器MCP服务器
"""
from fastapi import APIRouter
from mcp_servers.text_processor.models import (
    TextProcessRequest,
    TextProcessResponse
)
from utils.logger import logger

router = APIRouter(tags=["Text Processor"])


def process_text(action: str, text: str, remove_spaces: bool = False):
    """处理文本逻辑"""
    try:
        if action == "uppercase":
            result = text.upper()
        elif action == "lowercase":
            result = text.lower()
        elif action == "reverse":
            result = text[::-1]
        else:
            raise ValueError(f"Unknown action: {action}")
        
        if remove_spaces:
            result = result.replace(" ", "")
        
        return {
            "success": True,
            "original": text,
            "processed": result,
            "stats": {
                "original_length": len(text),
                "processed_length": len(result),
                "action": action
            },
            "error": None
        }
    except Exception as e:
        logger.error(f"文本处理失败: {str(e)}")
        return {
            "success": False,
            "original": text,
            "processed": None,
            "stats": None,
            "error": str(e)
        }


@router.post("/process", response_model=TextProcessResponse)
async def process_text_request(request: TextProcessRequest):
    """处理文本请求"""
    logger.info(f"处理文本: {request.action} - {request.text[:50]}...")
    result = process_text(request.action, request.text, request.remove_spaces)
    return TextProcessResponse(**result)


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "Text Processor",
        "version": "1.0.0"
    }


def get_info():
    """返回服务信息"""
    return {
        "name": "Text Processor",
        "version": "1.0.0",
        "description": "文本处理和转换工具",
        "endpoints": [
            {
                "path": "/text_processor/process",
                "method": "POST",
                "description": "处理文本"
            }
        ],
        "capabilities": [
            "大小写转换",
            "文本反转",
            "空格移除",
            "统计信息"
        ]
    }
```

#### 4. 注册到系统
```python
# config/settings.py
MCP_SERVERS_CONFIG = {
    # ... 其他服务
    "text_processor": {
        "name": "Text Processor",
        "description": "Text processing and conversion tools",
        "enabled": True,
        "version": "1.0.0",
        "module": "mcp_servers.text_processor.server",
        "prefix": "/text_processor",
        "tags": ["text", "processor", "utility"]
    },
}
```

#### 5. 测试
```bash
# 转换为大写
curl -X POST http://localhost:51234/text_processor/process \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "action": "uppercase"}'

# 转换为小写并移除空格
curl -X POST http://localhost:51234/text_processor/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World", "action": "lowercase", "remove_spaces": true}'
```

---

## 🎯 最佳实践

### 1. 代码组织

#### ✅ 推荐做法
```python
# 清晰的模块结构
mcp_servers/my_service/
├── __init__.py      # 只导出 router 和 get_info
├── server.py        # 路由和业务逻辑
└── models.py        # 数据模型定义
```

#### ❌ 避免做法
```python
# 不要在 __init__.py 中定义业务逻辑
# 不要混合多个服务的代码
# 不要使用硬编码的配置
```

### 2. 错误处理

#### ✅ 推荐做法
```python
try:
    result = process_logic()
    return {"success": True, "data": result}
except Exception as e:
    logger.error(f"处理失败: {str(e)}")
    return {"success": False, "error": str(e)}
```

#### ❌ 避免做法
```python
# 不要忽略错误
try:
    result = process_logic()
except:
    pass  # 静默失败

# 不要暴露敏感信息
return {"success": False, "error": str(sys.exc_info())}
```

### 3. 日志记录

#### ✅ 推荐做法
```python
from utils.logger import logger

# 记录关键操作
logger.info(f"处理请求: {request_id}")
logger.warning(f"性能警告: 处理时间 {duration}ms")
logger.error(f"处理失败: {error_message}")
```

#### ❌ 避免做法
```python
# 不要过度记录
logger.debug(f"每一步都要记录...")

# 不要记录敏感信息
logger.info(f"用户密码: {password}")  # 危险！
```

### 4. API 设计

#### ✅ 推荐做法
```python
# 使用标准HTTP方法
@router.post("/process")    # 创建/处理
@router.get("/status")      # 查询
@router.put("/update")      # 更新
@router.delete("/remove")   # 删除

# 使用响应模型
@router.post("/process", response_model=MyResponse)
async def process(request: MyRequest):
    return MyResponse(**result)
```

#### ❌ 避免做法
```python
# 不要使用不明确的端点
@router.post("/do_something")  # 不清晰

# 不要忽略返回类型
async def process(request):
    return result  # 类型不明确
```

### 5. 性能优化

#### ✅ 推荐做法
```python
# 使用异步操作
async def process_large_file(file_path: str):
    async with aiofiles.open(file_path, 'r') as f:
        content = await f.read()
    return process_content(content)

# 使用缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(param: str):
    return complex_calculation(param)
```

#### ❌ 避免做法
```python
# 不要在热路径上同步I/O
def process_large_file(file_path: str):
    with open(file_path, 'r') as f:
        content = f.read()  # 阻塞
    return process_content(content)
```

### 6. 安全考虑

#### ✅ 推荐做法
```python
# 验证输入
from pydantic import Field, validator

class SecureRequest(BaseModel):
    filename: str = Field(..., max_length=255)
    
    @validator('filename')
    def validate_filename(cls, v):
        # 防止路径穿越攻击
        if '..' in v or v.startswith('/'):
            raise ValueError('Invalid filename')
        return v

# 限制资源使用
import resource
resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024, -1))
```

#### ❌ 避免做法
```python
# 不要信任用户输入
filename = request.filename  # 可能包含 ../../../etc/passwd

# 不要无限制地使用资源
while True:
    data = fetch_more_data()  # 可能导致内存溢出
```

---

## ❓ 常见问题

### Q1: 服务无法启动

**症状**: 服务状态显示"未运行"或"启动失败"

**解决方案**:
```bash
# 1. 检查 Python 模块是否正确
python -c "from mcp_servers.my_service.server import get_info; print(get_info())"

# 2. 检查日志
tail -50 logs/mcp_server.log | grep -A 10 "my_service"

# 3. 手动测试导入
python -c "import mcp_servers.my_service; print(dir(mcp_servers.my_service))"
```

### Q2: API 端点无法访问

**症状**: 404 Not Found 或连接被拒绝

**解决方案**:
```bash
# 1. 检查服务是否运行
curl http://localhost:51234/health

# 2. 检查端口分配
curl http://localhost:51234/api/v1/servers/my_service/status

# 3. 检查路由前缀
curl http://localhost:YOUR_PORT/health  # 使用分配的端口
```

### Q3: Dashboard 中没有显示我的服务

**症状**: Dashboard 服务器列表中看不到新服务

**解决方案**:
```bash
# 1. 检查配置是否启用
grep -A 10 "my_service" config/settings.py
# 确保 "enabled": True

# 2. 重启系统
./start_safe.sh

# 3. 清除浏览器缓存
# 按 Cmd+Shift+R (Mac) 或 Ctrl+Shift+R (Windows)
```

### Q4: 导入错误

**症状**: `ModuleNotFoundError: No module named 'mcp_servers.my_service'`

**解决方案**:
```bash
# 1. 检查文件结构
ls -la mcp_servers/my_service/

# 2. 确保所有文件存在
ls mcp_servers/my_service/__init__.py
ls mcp_servers/my_service/server.py
ls mcp_servers/my_service/models.py

# 3. 检查 Python 路径
python -c "import sys; print('\n'.join(sys.path))"

# 4. 重新安装项目
pip install -e .
```

### Q5: 依赖库冲突

**症状**: 版本冲突或功能异常

**解决方案**:
```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 2. 升级 pip
pip install --upgrade pip

# 3. 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 4. 检查依赖版本
pip list | grep package_name
```

---

## 📖 相关文档

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - 快速开始指南
- **[API_REFERENCE.md](API_REFERENCE.md)** - API 参考手册
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系统架构详解
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 故障排除指南

---

## 🎓 进阶主题

### 1. 添加数据库支持

```python
# 在 server.py 中添加数据库操作
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('my_service.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.post("/save")
async def save_data(data: dict):
    conn = get_db_connection()
    conn.execute('INSERT INTO data (content) VALUES (?)', (str(data),))
    conn.commit()
    conn.close()
    return {"success": True}
```

### 2. 添加文件上传

```python
from fastapi import UploadFile, File
import aiofiles

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    return {"filename": file.filename, "path": file_path}
```

### 3. 添加异步任务

```python
import asyncio
from fastapi import BackgroundTasks

async def long_running_task(task_id: str):
    await asyncio.sleep(60)  # 模拟长时间任务
    logger.info(f"任务 {task_id} 完成")

@router.post("/start-task")
async def start_task(background_tasks: BackgroundTasks):
    task_id = "task_" + str(int(time.time()))
    background_tasks.add_task(long_running_task, task_id)
    return {"task_id": task_id, "status": "started"}
```

---

## 🚀 下一步

现在你已经掌握了创建 MCP Server 模块的完整流程：

1. ✅ **创建基础模块**: 参考本文档的示例代码
2. ✅ **实现核心功能**: 根据你的需求定制业务逻辑
3. ✅ **注册到系统**: 更新配置和 Dashboard
4. ✅ **测试验证**: 确保一切正常工作
5. ✅ **文档编写**: 为你的服务编写使用文档

### 持续改进

- 📊 **性能监控**: 添加性能指标收集
- 🔒 **安全加固**: 实施认证和授权
- 🧪 **单元测试**: 编写测试用例
- 📝 **API 文档**: 完善接口说明
- 🔄 **版本管理**: 使用语义化版本号

---

**💡 提示**: 创建 MCP Server 模块是一个迭代过程。先实现基础功能，然后逐步完善和优化！

**🎉 恭喜！** 你现在可以创建自己的 MCP Server 模块了。开始构建你的服务吧！
