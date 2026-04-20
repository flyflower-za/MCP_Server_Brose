# 🔧 问题修复总结

**修复时间**: 2026-04-21
**问题**: pdf_extractor 启动失败（退出码 1）
**状态**: ✅ 已完全解决

---

## 🎯 问题根因

### 1. **端口被占用**
- 端口 51238 被之前的僵尸进程占用
- 旧进程未正确清理

### 2. **子进程错误输出丢失**
- `process_manager.py` 中 `subprocess.Popen` 将 stderr 重定向到 PIPE
- 导致错误信息无法在主日志中看到

### 3. **缺少导入**
- 修改后的代码使用了 `settings.LOG_DIR` 但未导入 `settings`

---

## ✅ 已完成的修复

### 1. **[utils/process_manager.py](utils/process_manager.py)** - 进程管理器改进

#### 修复 1.1: 添加 settings 导入
```python
# 修改前
from utils.logger import logger
from utils.port_allocator import get_port_allocator
from config.port_config import get_fixed_port

# 修改后
from utils.logger import logger
from utils.port_allocator import get_port_allocator
from config.port_config import get_fixed_port
from config import settings  # ✅ 新增
```

#### 修复 1.2: 改进错误日志捕获
```python
# 修改前
process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,  # ❌ 错误输出丢失
    start_new_session=True
)
if process.poll() is None:
    return process.pid
else:
    logger.error(f"进程启动失败，退出码: {process.returncode}")
    # ❌ 看不到具体错误

# 修改后
log_file = settings.LOG_DIR / f"{server_id}_process.log"
process = subprocess.Popen(
    cmd,
    stdout=log_file.open('a'),  # ✅ 输出到日志文件
    stderr=log_file.open('a'),  # ✅ 错误也输出到日志文件
    start_new_session=True
)
if process.poll() is None:
    logger.info(f"✓ 进程启动成功，日志: {log_file}")
    return process.pid
else:
    # ✅ 读取并显示错误日志
    if log_file.exists():
        with log_file.open('r') as f:
            lines = f.readlines()
            error_msg = ''.join(lines[-20:])
        if error_msg:
            logger.error(f"错误输出:\n{error_msg}")
    return None
```

### 2. **[stop.sh](stop.sh)** - 停止脚本改进

#### 新增功能
- ✅ 彻底清理服务器端口范围（51235-51299）
- ✅ 清理 server_launcher 子进程
- ✅ 清理 main.py 进程
- ✅ 验证清理结果
- ✅ 清理 PID 文件

#### 使用方法
```bash
bash stop.sh
```

#### 输出示例
```
🛑 停止 MCP 服务器
========================================

📡 停止 API 网关 (端口 51234)...
✅ 已停止 API 网关

🧩 停止 MCP 服务器进程...
✅ 已停止端口 51238 上的进程

🔧 停止 server_launcher 子进程...
✅ 已停止 server_launcher 进程

📋 停止 main.py 进程...
✅ 已停止 main.py 进程

⏳ 等待进程完全退出...

🔍 验证清理结果...
✅ 端口 51234 已释放
✅ 端口 51238 已释放

🗑️  已清理 PID 文件

========================================
✅ 所有进程已停止
✅ 端口已全部释放
========================================
```

### 3. **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - 故障排除文档

新建完整的故障排除指南，包含：
- ✅ 常见问题及解决方案
- ✅ 诊断工具脚本
- ✅ 快速修复命令
- ✅ 预防措施

### 4. **[README.md](README.md)** - 更新文档

- ✅ 添加故障排除章节
- ✅ 快速修复命令
- ✅ 文档链接更新

---

## 🧪 验证测试

### 测试结果
```bash
=== 启动日志 ===
2026-04-21 00:21:39 - mcp_hub - INFO - 启动 MCP Servers Hub v1.0.0
2026-04-21 00:21:39 - mcp_hub - INFO - 架构: 进程隔离模式
2026-04-21 00:21:39 - mcp_hub - INFO - 开始启动MCP服务器，共 1 个已启用
2026-04-21 00:21:41 - mcp_hub - INFO - ✓ 进程启动成功，日志: .../logs/pdf_extractor_process.log
2026-04-21 00:21:41 - mcp_hub - INFO - ✅ 成功启动服务器 pdf_extractor (PID: 76698, Port: 51238)
2026-04-21 00:21:41 - mcp_hub - INFO - MCP服务器启动完成: 1/1 成功

=== 进程状态检查 ===
✅ Hub (51234) 正在运行
✅ PDF (51238) 正在运行
```

### 健康检查
```bash
# Hub 健康检查
curl http://localhost:51234/health
# ✅ 返回: {"status":"healthy","architecture":"process_isolation",...}

# PDF 提取器健康检查
curl http://localhost:51238/health
# ✅ 返回: {"status":"healthy","server_id":"pdf_extractor"}
```

---

## 📋 文件变更清单

| 文件 | 状态 | 说明 |
|------|------|------|
| `utils/process_manager.py` | ✏️ 修改 | 添加 settings 导入，改进错误日志 |
| `stop.sh` | ✏️ 修改 | 彻底清理所有进程和端口 |
| `docs/TROUBLESHOOTING.md` | ✨ 新建 | 故障排除指南 |
| `README.md` | ✏️ 修改 | 添加故障排除章节 |
| `.env.example` | ✏️ 修改 | 更新端口配置 |
| `dashboard/index.html` | ✏️ 修改 | 自动检测 Hub Base URL |
| `requirements.txt` | ✏️ 修改 | 优化依赖清单 |

---

## 🚀 现在可以正常使用

### 启动系统
```bash
# 彻底清理旧进程
bash stop.sh

# 启动系统
./start_safe.sh
```

### 访问服务
- **主页**: http://localhost:51234
- **API 文档**: http://localhost:51234/docs
- **Dashboard**: http://localhost:51234/dashboard
  - 用户名: `admin`
  - 密码: `brose123`
- **PDF 提取器**: http://localhost:51238/docs

### 停止系统
```bash
bash stop.sh
```

---

## 📈 改进效果

### 修复前
- ❌ pdf_extractor 启动失败
- ❌ 看不到错误信息（退出码 1）
- ❌ 需要手动清理端口
- ❌ 没有故障排除文档

### 修复后
- ✅ 所有服务正常启动
- ✅ 错误信息清晰可见
- ✅ 一键清理所有进程
- ✅ 完整的故障排除指南

---

## 🔍 未来建议

### 短期改进
1. 添加进程监控自动重启
2. 改进日志轮转机制
3. 添加启动失败重试逻辑

### 长期改进
1. 添加进程资源限制（CPU、内存）
2. 实现进程健康检查和自动恢复
3. 添加性能监控面板

---

**问题解决**: ✅ 完成
**测试状态**: ✅ 通过
**文档更新**: ✅ 完成
