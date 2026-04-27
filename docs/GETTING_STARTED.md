# 🚀 MCP Servers Hub - 快速开始指南

欢迎使用 MCP Servers Hub！本指南将帮助你快速上手并开始使用这个统一的MCP服务器管理系统。

## 📋 目录

- [系统要求](#系统要求)
- [快速安装](#快速安装)
- [启动方式](#启动方式)
- [基础配置](#基础配置)
- [访问控制台](#访问控制台)
- [常见问题](#常见问题)

---

## 🎯 系统要求

### 必需环境
- **Python**: 3.8 或更高版本
- **操作系统**: macOS, Linux, Windows
- **内存**: 至少 2GB 可用内存
- **磁盘**: 至少 500MB 可用空间

### 可选依赖
- **PM2**: 进程管理器（用于生产环境）
- **Git**: 版本控制（推荐）

---

## ⚡ 快速安装

### 1. 克隆项目
```bash
git clone <repository-url>
cd MCP_Server_Brose
```

### 2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境
```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置（可选）
vim .env
```

### 5. 初始化系统
```bash
# 创建必要的目录
mkdir -p logs
```

---

## 🚀 启动方式

### 方式1：一键启动（推荐）

#### 使用安全启动脚本
```bash
./start_safe.sh
```

**优点：**
- ✅ 自动检查环境
- ✅ 自动处理端口冲突
- ✅ 自动创建必要目录
- ✅ 详细的错误提示

#### 使用PM2启动（生产环境）
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 方式2：手动启动

#### 直接运行Python
```bash
python main.py
```

#### 使用Uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 51234
```

### 方式3：开发模式

#### 启用调试模式
```bash
# 在 .env 中设置
MCP_DEBUG=true

# 启动服务器
python main.py
```

---

## ⚙️ 基础配置

### 修改Hub端口

#### 编辑配置文件
```bash
vim .env
```

#### 修改端口配置
```bash
# 将默认端口改为其他端口
MCP_PORT=51234  # 改为你想要的端口
```

#### 重启服务器
```bash
./start_safe.sh
```

### Dashboard登录配置

#### 设置管理员账户
```bash
# 在 .env 中配置
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=your_secure_password
```

#### 设置JWT密钥
```bash
# 生成随机密钥
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 添加到 .env
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY" >> .env
```

### 日志配置

#### 调整日志级别
```bash
# 在 .env 中设置
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

#### 查看日志
```bash
# 实时查看日志
tail -f logs/mcp_server.log

# 查看最近50行
tail -n 50 logs/mcp_server.log
```

---

## 🌐 访问控制台

### Dashboard访问

#### 打开控制台
```bash
# 默认地址
open http://localhost:51234/dashboard

# 或在浏览器中访问
http://localhost:51234/dashboard
```

#### 登录凭据
- **用户名**: admin (或你在 .env 中设置的用户名)
- **密码**: pdf123 (或你在 .env 中设置的密码)

### API文档访问

#### Swagger UI
```bash
http://localhost:51234/docs
```

#### ReDoc
```bash
http://localhost:51234/redoc
```

### 健康检查

#### API端点
```bash
curl http://localhost:51234/health
```

#### 预期响应
```json
{
  "status": "healthy",
  "architecture": "process_isolation",
  "loaded_servers": 2,
  "running_servers": 2
}
```

---

## 🔧 首次使用

### 1. 登录Dashboard
1. 打开浏览器访问 `http://localhost:51234/dashboard`
2. 输入管理员凭据登录
3. 勾选"记住我"选项（7天免登录）

### 2. 检查服务器状态
- 查看**服务器列表**中的各个服务状态
- 确认**运行中服务**数量
- 检查**健康状态**面板

### 3. 测试功能

#### PDF提取测试
1. 在侧边栏找到 **PDF提取测试** 面板
2. 输入PDF URL
3. 点击"开始提取"
4. 查看提取结果

#### 二维码识别测试
1. 在侧边栏找到 **二维码识别测试** 面板
2. 输入图片URL或Base64数据
3. 点击"识别二维码"
4. 查看识别结果

### 4. 配置管理（可选）

#### 固定服务器端口
1. 在服务器卡片中找到**固定端口**配置区域
2. 点击"锁定/编辑"按钮
3. 输入想要的端口号
4. 点击"保存"

#### 添加新服务器
1. 点击**配置管理**面板中的"+添加"按钮
2. 填写服务器信息
3. 保存配置

---

## 🛠️ 常用命令

### 服务器管理

#### 启动所有服务
```bash
./start_safe.sh
# 或
pm2 start ecosystem.config.js
```

#### 停止所有服务
```bash
# PM2方式
pm2 stop all

# 手动方式
pkill -f "python.*main.py"
```

#### 重启服务
```bash
# PM2方式
pm2 restart all

# 手动方式
./scripts/restart.sh
```

### 状态检查

#### 检查服务状态
```bash
# PM2方式
pm2 status

# API方式
curl http://localhost:51234/api/v1/servers/statuses
```

#### 检查端口占用
```bash
# macOS/Linux
lsof -i :51234

# 或使用netstat
netstat -an | grep 51234
```

### 日志查看

#### PM2日志
```bash
# 所有日志
pm2 logs

# 特定服务
pm2 logs mcp-hub
```

#### 系统日志
```bash
# 实时监控
tail -f logs/mcp_server.log

# 错误日志
grep ERROR logs/mcp_server.log
```

---

## ❓ 常见问题

### Q1: 端口已被占用
**错误**: `Address already in use`

**解决方案**:
```bash
# 1. 查找占用端口的进程
lsof -i :51234

# 2. 杀死进程
kill -9 <PID>

# 3. 或修改配置文件中的端口
vim .env
# 修改 MCP_PORT=其他端口
```

### Q2: 依赖安装失败
**错误**: `No module named 'xxx'`

**解决方案**:
```bash
# 1. 确保虚拟环境已激活
source .venv/bin/activate

# 2. 重新安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 3. 如果特定包失败，单独安装
pip install <package_name>
```

### Q3: 无法访问Dashboard
**症状**: 浏览器显示"连接被拒绝"

**解决方案**:
```bash
# 1. 检查服务是否运行
curl http://localhost:51234/health

# 2. 检查端口是否正确
cat .env | grep MCP_PORT

# 3. 检查防火墙设置
# 4. 确认使用正确的地址和端口
```

### Q4: 登录失败
**症状**: "用户名或密码错误"

**解决方案**:
```bash
# 1. 检查.env文件中的配置
cat .env | grep DASHBOARD

# 2. 重置密码
echo "DASHBOARD_USERNAME=admin" >> .env
echo "DASHBOARD_PASSWORD=admin123" >> .env

# 3. 重启服务
./start_safe.sh
```

### Q5: MCP服务器无法启动
**症状**: 服务器状态显示"未运行"

**解决方案**:
```bash
# 1. 查看日志找错误
tail -20 logs/mcp_server.log

# 2. 检查端口冲突
./scripts/check_startup.sh

# 3. 手动启动单个服务器
curl -X POST http://localhost:51234/api/v1/servers/<server_id>/start

# 4. 检查Python模块是否正确
python -c "from mcp_servers.pdf_extractor.server import get_info; print(get_info())"
```

---

## 📚 下一步

现在你已经成功启动了MCP Servers Hub，可以继续学习：

### 📖 推荐阅读顺序
1. **[PORT_GUIDE.md](PORT_GUIDE.md)** - 了解端口管理和配置
2. **[API_REFERENCE.md](API_REFERENCE.md)** - 学习API使用方法
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - 理解系统架构
4. **[N8N_INTEGRATION.md](N8N_INTEGRATION.md)** - 集成到n8n工作流

### 🎯 实用指南
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - 故障排除指南
- **[CONFIG_PERSISTENCE.md](CONFIG_PERSISTENCE.md)** - 配置持久化
- **[QR_CODE_READER.md](QR_CODE_READER.md)** - 二维码识别器使用

### 🔗 外部集成
- **[client_example.py](../client_example.py)** - 客户端代码示例

---

## 💡 提示

### 开发环境
```bash
# 启用调试模式
export MCP_DEBUG=true
python main.py
```

### 生产环境
```bash
# 使用PM2管理
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 安全建议
- 修改默认密码
- 使用强密码
- 启用HTTPS（生产环境）
- 定期更新依赖

---

## 🆘 获取帮助

如果遇到问题：
1. 查看 **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** 故障排除指南
2. 检查 `logs/mcp_server.log` 日志文件
3. 访问 GitHub Issues 提问
4. 查阅 API 文档: `http://localhost:51234/docs`

---

**恭喜！** 🎉 你已经成功启动了MCP Servers Hub系统。开始探索强大的功能吧！
