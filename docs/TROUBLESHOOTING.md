# 故障排除指南

## 常见问题及解决方案

---

### 🔴 问题 1: pdf_extractor 启动失败（退出码 1）

#### 症状
```
2026-04-21 00:19:29 - mcp_hub - ERROR - 进程启动失败，退出码: 1
2026-04-21 00:19:29 - mcp_hub - WARNING - 启动失败的服务器: pdf_extractor
```

#### 原因分析
1. **端口被占用** - 之前的进程没有正确关闭
2. **虚拟环境未激活** - 子进程无法找到依赖
3. **模块导入失败** - 依赖未安装

#### 解决方案

**步骤 1: 检查端口占用**
```bash
# 检查固定端口 (51238)
lsof -ti :51238

# 检查 Hub 端口 (51234)
lsof -ti :51234

# 检查服务器端口范围
lsof -ti :51235-51299
```

**步骤 2: 彻底清理所有进程**
```bash
# 使用改进的停止脚本
bash stop.sh
```

**步骤 3: 手动清理（如果 stop.sh 无效）**
```bash
# 杀死所有相关进程
pkill -9 -f "server_launcher"
pkill -9 -f "main.py"
lsof -ti :51234 | xargs kill -9
lsof -ti :51238 | xargs kill -9
```

**步骤 4: 重新启动**
```bash
# 使用启动脚本（会自动激活虚拟环境）
./start_safe.sh
```

---

### 🔴 问题 2: 端口已被占用

#### 症状
```
ERROR: [Errno 48] error while attempting to bind on address ('0.0.0.0', 51238): address already in use
```

#### 解决方案

**方法 1: 使用 stop.sh（推荐）**
```bash
bash stop.sh
```

**方法 2: 手动释放特定端口**
```bash
# 查找占用端口的进程
lsof -i :51238

# 杀死进程
lsof -ti :51238 | xargs kill -9

# 或使用端口范围清理
for p in $(seq 51235 51299); do
    lsof -ti :$p | xargs kill -9 2>/dev/null
done
```

**方法 3: 更改固定端口配置**
```bash
# 访问 Dashboard
http://localhost:51234/dashboard

# 在服务器卡片中：
# 1. 点击 "✏️ 锁定 / 编辑"
# 2. 输入新端口号（如 51240）
# 3. 点击 "保存"
# 4. 重启服务器
```

---

### 🔴 问题 3: 虚拟环境依赖缺失

#### 症状
```
ModuleNotFoundError: No module named 'fastapi'
```

#### 解决方案

**检查虚拟环境**
```bash
# 确认虚拟环境存在
ls -la .venv/

# 激活虚拟环境
source .venv/bin/activate

# 验证 Python 路径
which python
# 应该显示: /path/to/MCP_Server_Brose/.venv/bin/python
```

**重新安装依赖**
```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 验证关键依赖
python -c "import fastapi, uvicorn, pydantic; print('✅ 依赖正常')"
```

---

### 🔴 问题 3: Dashboard 无法连接

#### 症状
- Dashboard 显示 "Hub 离线"
- 请求失败: `Connection refused`

#### 解决方案

**步骤 1: 检查 Hub 是否运行**
```bash
# 检查端口
lsof -ti :51234

# 测试健康检查
curl http://localhost:51234/health
```

**步骤 2: 检查防火墙**
```bash
# macOS
sudo pfctl -d  # 临时禁用防火墙测试

# Linux
sudo ufw status
sudo ufw allow 51234
```

**步骤 3: 检查 .env 配置**
```bash
# 确认端口配置
cat .env | grep MCP_PORT

# 应该显示:
# MCP_PORT=51234
```

**步骤 4: 清除浏览器缓存**
- 按 `Cmd+Shift+R` (macOS) 或 `Ctrl+Shift+R` (Windows) 强制刷新
- 或使用无痕模式重新访问

---

### 🔴 问题 4: 进程启动后立即退出

#### 症状
```
INFO: Started server process [12345]
INFO: Waiting for application startup.
INFO: Application startup complete.
# 然后立即退出
```

#### 解决方案

**检查子进程日志**
```bash
# 查看 PDF 提取器日志
cat logs/pdf_extractor_process.log

# 查看主日志
tail -f logs/mcp_server.log
```

**常见错误**
1. **端口被占用** - 参见问题 2
2. **权限问题** - 确保有日志目录写权限
3. **配置错误** - 检查 `.env` 和 `config/server_ports.json`

---

### 🔴 问题 5: 日志文件过大

#### 症状
- `logs/mcp_server.log` 文件过大
- 磁盘空间不足

#### 解决方案

**清理旧日志**
```bash
# 备份当前日志
cp logs/mcp_server.log logs/mcp_server.log.backup

# 清空日志
> logs/mcp_server.log
> logs/pdf_extractor_process.log

# 或删除旧日志
rm logs/*.log.*
```

**配置日志轮转**
编辑 `utils/logger.py`:
```python
from logging.handlers import RotatingFileHandler

# 每个文件最大 10MB，保留 5 个备份
handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

---

## 🔧 诊断工具

### 完整诊断脚本
```bash
#!/bin/bash

echo "🔍 MCP Servers Hub 诊断工具"
echo "========================================"

# 1. Python 环境
echo ""
echo "📦 Python 环境:"
source .venv/bin/activate
python --version
which python

# 2. 依赖检查
echo ""
echo "📚 依赖检查:"
python -c "import fastapi, uvicorn, pydantic, requests, httpx, pypdf2, psutil, dotenv" 2>&1 && echo "✅ 所有依赖已安装" || echo "❌ 依赖缺失"

# 3. 端口检查
echo ""
echo "🔌 端口状态:"
for port in 51234 51238; do
    if lsof -ti :$port > /dev/null 2>&1; then
        echo "✅ 端口 $port: $(lsof -ti :$port | head -1)"
    else
        echo "❌ 端口 $port: 未使用"
    fi
done

# 4. 进程检查
echo ""
echo "🔧 进程状态:"
pgrep -f "main.py" > /dev/null && echo "✅ Hub 进程运行中" || echo "❌ Hub 进程未运行"
pgrep -f "server_launcher" > /dev/null && echo "✅ 服务器进程运行中" || echo "❌ 服务器进程未运行"

# 5. 配置文件
echo ""
echo "⚙️  配置文件:"
[ -f .env ] && echo "✅ .env 存在" || echo "❌ .env 缺失"
[ -f config/server_ports.json ] && echo "✅ server_ports.json 存在" || echo "❌ server_ports.json 缺失"

# 6. 日志目录
echo ""
echo "📋 日志目录:"
[ -d logs ] && echo "✅ logs 目录存在" || echo "❌ logs 目录缺失"

echo ""
echo "========================================"
echo "诊断完成"
```

### 快速修复命令
```bash
# 一键修复所有常见问题
bash stop.sh && \
source .venv/bin/activate && \
pip install -q -r requirements.txt && \
./start_safe.sh
```

---

## 📞 获取帮助

如果以上方案都无法解决问题：

1. **收集日志**
   ```bash
   # 收集所有日志
   tar -czf debug_logs.tar.gz logs/

   # 收集进程信息
   ps aux | grep python > process_info.txt

   # 收集端口信息
   lsof -i :51234-51299 > port_info.txt
   ```

2. **检查系统信息**
   ```bash
   # Python 版本
   python --version

   # 操作系统
   uname -a

   # 依赖版本
   pip list | grep -E "(fastapi|uvicorn|pydantic)"
   ```

3. **查看完整配置**
   ```bash
   cat .env
   cat config/server_ports.json
   cat config/settings.py | grep -A 5 "class Settings"
   ```

---

## ✅ 预防措施

### 1. 使用启动脚本
```bash
# 始终使用启动脚本而不是直接运行
./start_safe.sh  # ✅ 推荐
python main.py   # ❌ 不推荐（可能未激活虚拟环境）
```

### 2. 正确停止服务
```bash
# 使用停止脚本而不是直接杀死进程
bash stop.sh  # ✅ 推荐
kill -9 $(pgrep main.py)  # ❌ 不推荐（可能留下僵尸进程）
```

### 3. 定期清理
```bash
# 定期清理旧日志
find logs/ -name "*.log.*" -mtime +7 -delete

# 定期清理 Python 缓存
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
```

### 4. 备份配置
```bash
# 备份重要配置
cp .env .env.backup
cp config/server_ports.json config/server_ports.json.backup
```

---

**最后更新**: 2026-04-21
**版本**: 1.0.0
