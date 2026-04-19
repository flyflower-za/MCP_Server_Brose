# 🚀 MCP服务器启动完整指南

## 📋 启动前检查清单

### 1️⃣ 确认项目结构
```bash
# 查看当前目录
pwd
# 应该在: /Users/zhouao/Projects/WorkSpace/AI/MCP_Server

# 查看必要文件是否存在
ls -la main.py config/settings.py requirements.txt
```

### 2️⃣ 检查Python环境
```bash
# 检查Python版本
python --version
# 需要: Python 3.8+

# 检查虚拟环境
ls -la .venv/
```

### 3️⃣ 安装依赖
```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 验证关键包
python -c "import fastapi, uvicorn, pypdf2, requests; print('✅ 依赖安装成功')"
```

---

## 🎯 启动方式

### 方式1：使用启动脚本（推荐）

```bash
# 最简单的方式
./start.sh
```

### 方式2：直接运行Python

```bash
# 激活虚拟环境（如果还没激活）
source .venv/bin/activate

# 启动服务器
python main.py
```

### 方式3：使用环境变量定制

```bash
# 自定义端口启动
MCP_PORT=9000 python main.py

# 启用调试模式
MCP_DEBUG=true python main.py

# 设置日志级别
LOG_LEVEL=DEBUG python main.py

# 组合使用
MCP_PORT=9000 LOG_LEVEL=DEBUG MCP_DEBUG=true python main.py
```

### 方式4：使用uvicorn直接启动

```bash
# 开发环境（自动重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产环境（多worker）
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 详细日志
uvicorn main:app --log-level debug
```

### 方式5：使用gunicorn（生产环境）

```bash
# 安装gunicorn
pip install gunicorn

# 启动
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

---

## ✅ 启动成功验证

### 1️⃣ 检查启动日志

启动成功后，你会看到类似的日志：

```
============================================================
启动 MCP Servers Hub v1.0.0
============================================================
开始加载MCP服务器，共 1 个已启用
✅ 成功加载MCP服务器: pdf_extractor (mcp_servers.pdf_extractor.server)
MCP服务器加载完成: 1/1 成功
服务器将在 0.0.0.0:8000 启动
API文档: http://0.0.0.0:8000/docs
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 2️⃣ 测试系统端点

```bash
# 测试根路径
curl http://localhost:8000/

# 测试健康检查
curl http://localhost:8000/health

# 测试服务器列表
curl http://localhost:8000/servers
```

### 3️⃣ 访问API文档

```bash
# 在浏览器中打开
open http://localhost:8000/docs

# 或者
open http://localhost:8000/redoc
```

### 4️⃣ 运行客户端测试

```bash
# 在新终端中运行
python client_example.py
```

---

## 🔧 故障排除

### 问题1：端口被占用

**错误信息：**
```
OSError: [Errno 48] Address already in use
```

**解决方案：**
```bash
# 方法1：使用其他端口
MCP_PORT=8001 python main.py

# 方法2：找到并停止占用端口的进程
lsof -i :8000
kill -9 <PID>

# 方法3：等待几秒后重试
sleep 5 && python main.py
```

### 问题2：模块导入错误

**错误信息：**
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案：**
```bash
# 重新安装依赖
pip install -r requirements.txt

# 或单独安装缺失的包
pip install fastapi uvicorn pypdf2 requests pydantic
```

### 问题3：权限错误

**错误信息：**
```
PermissionError: [Errno 13] Permission denied
```

**解决方案：**
```bash
# 给脚本执行权限
chmod +x start.sh

# 或直接用python运行
python main.py
```

### 问题4：配置文件错误

**错误信息：**
```
KeyError: 'MCP_SERVERS_CONFIG'
```

**解决方案：**
```bash
# 检查配置文件
cat config/settings.py

# 确认MCP_SERVERS_CONFIG存在
grep -n "MCP_SERVERS_CONFIG" config/settings.py
```

### 问题5：虚拟环境问题

**解决方案：**
```bash
# 重建虚拟环境
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📊 启动状态检查

### 创建检查脚本

```bash
# 创建启动检查脚本
cat > check_startup.sh << 'EOF'
#!/bin/bash

echo "🔍 MCP服务器启动检查"
echo "===================="

# 1. 检查进程
if pgrep -f "python main.py" > /dev/null; then
    echo "✅ 服务器进程运行中"
else
    echo "❌ 服务器进程未运行"
    exit 1
fi

# 2. 检查端口
if lsof -i :8000 > /dev/null 2>&1; then
    echo "✅ 端口8000已监听"
else
    echo "❌ 端口8000未监听"
    exit 1
fi

# 3. 检查HTTP响应
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ HTTP服务响应正常"
else
    echo "❌ HTTP服务无响应"
    exit 1
fi

# 4. 检查API端点
servers_count=$(curl -s http://localhost:8000/servers | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])")
echo "✅ 已加载 $servers_count 个MCP服务器"

echo "===================="
echo "🎉 所有检查通过！"
EOF

chmod +x check_startup.sh
```

---

## 🎯 后台运行

### 使用nohup
```bash
nohup python main.py > logs/server.log 2>&1 &
echo $! > logs/server.pid
```

### 使用screen
```bash
# 创建screen会话
screen -S mcp_server

# 在screen中启动服务器
python main.py

# 按Ctrl+A然后按D来分离会话

# 重新连接
screen -r mcp_server
```

### 使用systemd（Linux）

```bash
# 创建服务文件
sudo cat > /etc/systemd/system/mcp-server.service << 'EOF'
[Unit]
Description=MCP Server Hub
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/MCP_Server
Environment="PATH=/path/to/MCP_Server/.venv/bin"
ExecStart=/path/to/MCP_Server/.venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl start mcp-server
sudo systemctl enable mcp-server
sudo systemctl status mcp-server
```

---

## 📱 启动后访问

### 命令行访问
```bash
# 系统信息
curl http://localhost:8000/

# 健康检查
curl http://localhost:8000/health

# 服务器列表
curl http://localhost:8000/servers | python3 -m json.tool
```

### 浏览器访问
```
主页:           http://localhost:8000
API文档:        http://localhost:8000/docs
ReDoc文档:      http://localhost:8000/redoc
OpenAPI JSON:   http://localhost:8000/openapi.json
```

### Python客户端访问
```python
from client_example import MCPHubClient

client = MCPHubClient()
info = client.get_system_info()
print(f"系统: {info['system']}")
print(f"版本: {info['version']}")
```

---

## 🛑 停止服务器

### 优雅停止
```bash
# 在运行的终端按
Ctrl+C
```

### 强制停止
```bash
# 查找进程
ps aux | grep "python main.py"

# 停止进程
pkill -f "python main.py"

# 或使用PID
kill -9 <PID>
```

### 如果使用了PID文件
```bash
# 读取PID并停止
kill $(cat logs/server.pid)
```

---

## 🔄 重启服务器

### 快速重启
```bash
# 停止当前服务器
pkill -f "python main.py"

# 等待几秒
sleep 2

# 重新启动
python main.py
```

### 自动重启脚本
```bash
cat > restart.sh << 'EOF'
#!/bin/bash
echo "🔄 重启MCP服务器..."

# 停止
pkill -f "python main.py"
sleep 2

# 启动
nohup python main.py > logs/server.log 2>&1 &
echo $! > logs/server.pid

sleep 3

# 检查状态
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 重启成功"
else
    echo "❌ 重启失败"
fi
EOF

chmod +x restart.sh
```

---

## 📊 监控和日志

### 查看日志
```bash
# 实时查看系统日志
tail -f logs/mcp_server.log

# 查看最近100行
tail -n 100 logs/mcp_server.log

# 搜索错误日志
grep ERROR logs/mcp_server.log
```

### 监控脚本
```bash
cat > monitor.sh << 'EOF'
#!/bin/bash

while true; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ $(date '+%Y-%m-%d %H:%M:%S') - 服务器运行正常"
    else
        echo "❌ $(date '+%Y-%m-%d %H:%M:%S') - 服务器无响应"
    fi
    sleep 60
done
EOF

chmod +x monitor.sh
```

---

## 🎯 启动最佳实践

### 开发环境
```bash
# 使用自动重载
uvicorn main:app --reload --log-level debug
```

### 测试环境
```bash
# 使用指定端口
MCP_PORT=8001 python main.py
```

### 生产环境
```bash
# 使用gunicorn多进程
gunicorn main:app --workers 4 --bind 0.0.0.0:8000
```

---

## 📋 快速启动总结

### 🚀 最快的启动方式
```bash
# 1. 确保虚拟环境激活
source .venv/bin/activate

# 2. 启动服务器
python main.py

# 3. 验证（在新终端）
curl http://localhost:8000/health
```

### ✅ 启动成功的标志
1. 终端显示 "服务器将在 0.0.0.0:8000 启动"
2. 可以访问 http://localhost:8000
3. 健康检查返回 {"status": "healthy"}
4. API文档可以正常访问

记住：**启动后不要关闭终端，除非使用后台运行！**
