# 🔧 MCP服务器端口管理完全指南

## 📍 端口配置位置

### 1️⃣ **配置文件** (config/settings.py)
```python
class Settings:
    # 默认端口配置
    PORT: int = int(os.getenv("MCP_PORT", "8000"))
    HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
```

---

## 🔄 端口修改方法

### **方法1：环境变量（推荐）**

#### 临时修改
```bash
# 使用不同端口启动
MCP_PORT=9000 python main.py

# 同时设置多个参数
MCP_PORT=9000 MCP_HOST=127.0.0.1 python main.py
```

#### 永久修改
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export MCP_PORT=9000

# 重新加载配置
source ~/.bashrc  # 或 source ~/.zshrc

# 然后正常启动
python main.py
```

### **方法2：直接修改配置文件**

#### 编辑 config/settings.py
```python
class Settings:
    # 从默认8000改为9000
    PORT: int = int(os.getenv("MCP_PORT", "9000"))  # ← 改这里
```

#### 重启服务器
```bash
python main.py
```

### **方法3：命令行参数**

#### 使用uvicorn直接启动
```bash
# 开发环境
uvicorn main:app --port 9000 --reload

# 生产环境
uvicorn main:app --host 0.0.0.0 --port 9000 --workers 4
```

### **方法4：创建特定环境的启动脚本**

#### 开发环境脚本
```bash
# scripts/dev_start.sh
#!/bin/bash
export MCP_PORT=8000
export MCP_DEBUG=true
export LOG_LEVEL=DEBUG
python main.py
```

#### 测试环境脚本
```bash
# scripts/test_start.sh
#!/bin/bash
export MCP_PORT=8001
export LOG_FILE=test_server.log
python main.py
```

#### 生产环境脚本
```bash
# scripts/prod_start.sh
#!/bin/bash
export MCP_PORT=80
export MCP_DEBUG=false
export LOG_LEVEL=INFO
python main.py
```

---

## 🔍 端口检查和监控

### **检查端口占用**
```bash
# 检查特定端口
lsof -i :8000

# 检查多个端口
lsof -i :8000,8001,8002

# 查看所有Python进程占用的端口
lsof -i -P | grep Python | grep LISTEN
```

### **查找可用端口**
```bash
# 查找8000-8100范围内的可用端口
for port in {8000..8100}; do
    if ! lsof -i :$port > /dev/null 2>&1; then
        echo "端口 $port 可用"
        break
    fi
done
```

### **端口监控脚本**
```bash
# scripts/monitor_port.sh
#!/bin/bash

PORT=${1:-8000}

echo "监控端口 $PORT..."

while true; do
    if lsof -i :$PORT > /dev/null 2>&1; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 端口 $PORT 正在运行"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 端口 $PORT 未运行"
    fi
    sleep 10
done
```

---

## 🛠️ 端口冲突解决

### **自动端口冲突解决**
```bash
# scripts/start_with_auto_port.sh
#!/bin/bash

# 默认从8000开始尝试
START_PORT=8000
END_PORT=8100

for port in $(seq $START_PORT $END_PORT); do
    if ! lsof -i :$port > /dev/null 2>&1; then
        echo "✅ 找到可用端口: $port"
        MCP_PORT=$port python main.py
        exit 0
    fi
done

echo "❌ 无法找到可用端口 ($START_PORT-$END_PORT)"
exit 1
```

### **手动端口冲突解决**
```bash
# 1. 找到占用端口的进程
lsof -i :8000

# 2. 查看进程详情
ps aux | grep <PID>

# 3. 停止进程
kill <PID>          # 优雅停止
kill -9 <PID>       # 强制停止

# 4. 或者使用其他端口
MCP_PORT=8001 python main.py
```

---

## 🌐 多服务器端口分配

### **场景1：开发/测试/生产环境**
```bash
# 开发环境
export MCP_PORT=8000
python main.py

# 测试环境
export MCP_PORT=8001
python main.py

# 生产环境
export MCP_PORT=80
python main.py
```

### **场景2：多个服务实例**
```bash
# 实例1
export MCP_PORT=8000
python main.py &

# 实例2
export MCP_PORT=8001
python main.py &

# 实例3
export MCP_PORT=8002
python main.py &
```

### **场景3：不同类型的服务**
```bash
# PDF服务
export MCP_PORT=8000
python main.py --service pdf &

# 图片服务
export MCP_PORT=8001
python main.py --service image &

# 数据服务
export MCP_PORT=8002
python main.py --service data &
```

---

## 🔐 端口安全配置

### **开发环境**
```python
# config/settings.py
class Settings:
    # 仅本地访问
    HOST: str = "127.0.0.1"
    PORT: int = 8000
```

### **生产环境**
```python
# config/settings.py
class Settings:
    # 允许外部访问
    HOST: str = "0.0.0.0"
    PORT: int = 80  # 或443（HTTPS）
```

### **防火墙配置**
```bash
# 仅允许本地访问8000端口
sudo iptables -A INPUT -p tcp --dport 8000 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -j DROP

# 允许特定IP访问
sudo iptables -A INPUT -p tcp --dport 8000 -s 192.168.1.100 -j ACCEPT
```

---

## 📊 端口使用情况统计

### **端口使用统计脚本**
```bash
# scripts/port_stats.sh
#!/bin/bash

echo "📊 MCP服务器端口使用统计"
echo "========================"

# 检查常用端口
PORTS=(8000 8001 8002 8080 9000)

for port in "${PORTS[@]}"; do
    if lsof -i :$port > /dev/null 2>&1; then
        PID=$(lsof -ti :$port)
        CMD=$(ps -p $PID -o comm=)
        echo "✅ 端口 $port - 使用中 (PID: $PID, CMD: $CMD)"
    else
        echo "❌ 端口 $port - 空闲"
    fi
done
```

---

## 🚀 快速端口切换

### **创建端口切换别名**
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc

# 快速切换到不同端口
alias mcp-dev='export MCP_PORT=8000 && python main.py'
alias mcp-test='export MCP_PORT=8001 && python main.py'
alias mcp-prod='export MCP_PORT=80 && sudo python main.py'

# 快速重启
alias mcp-restart='pkill -f "python main.py" && sleep 2 && mcp-dev'

# 检查端口状态
alias mcp-status='lsof -i :8000 -i :8001 -i :8002'
```

### **使用方法**
```bash
# 开发环境
mcp-dev

# 测试环境
mcp-test

# 重启
mcp-restart

# 查看状态
mcp-status
```

---

## 🌍 Docker端口映射

### **Docker Compose配置**
```yaml
# docker-compose.yml
version: '3.8'
services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"   # 主端口
      - "8001:8001"   # 管理端口
    environment:
      - MCP_PORT=8000
      - MCP_HOST=0.0.0.0
```

### **Docker运行**
```bash
# 映射到不同端口
docker run -p 9000:8000 mcp-server

# 映射多个端口
docker run -p 8000:8000 -p 8001:8001 mcp-server
```

---

## 📱 端口配置最佳实践

### **推荐端口分配**
```
开发环境: 8000-8099
测试环境: 8100-8199
生产环境: 80 (HTTP), 443 (HTTPS)
管理接口: 8080-8099
```

### **端口选择原则**
1. **避免系统端口** (1-1023)
2. **避免常用服务端口**
   - 3306: MySQL
   - 5432: PostgreSQL
   - 6379: Redis
   - 9200: Elasticsearch
3. **使用连续端口范围**便于管理
4. **记录端口使用情况**避免冲突

### **环境变量命名规范**
```bash
# MCP服务器专用
export MCP_PORT=8000
export MCP_HOST=0.0.0.0

# 数据库相关
export DB_PORT=5432

# 缓存相关
export REDIS_PORT=6379
```

---

## 🎯 常见问题解决

### **问题1：端口被占用**
```bash
# 快速解决
MCP_PORT=8001 python main.py

# 或者清理端口
lsof -ti :8000 | xargs kill -9
```

### **问题2：权限不足**
```bash
# 使用1024以下端口需要sudo
sudo MCP_PORT=80 python main.py

# 或使用80端口重定向
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000
```

### **问题3：端口无法访问**
```bash
# 检查防火墙
sudo ufw status

# 开放端口
sudo ufw allow 8000

# 检查服务器绑定
curl http://localhost:8000  # 本地测试
curl http://127.0.0.1:8000  # 回环地址
```

---

## 📋 快速参考

| 操作 | 命令 |
|------|------|
| **修改端口** | `MCP_PORT=9000 python main.py` |
| **检查端口** | `lsof -i :8000` |
| **释放端口** | `lsof -ti :8000 \| xargs kill -9` |
| **查找可用端口** | `lsof -i :8000-8100` |
| **监控端口** | `watch -n 1 'lsof -i :8000'` |

---

## 💡 总结

**端口管理三要素：**
1. **配置** - 修改config/settings.py或使用环境变量
2. **检查** - 使用lsof命令监控端口状态
3. **解决** - 遇到冲突时及时切换或释放端口

**记住：** 8000是默认端口，但你可以自由修改为任何可用端口！
