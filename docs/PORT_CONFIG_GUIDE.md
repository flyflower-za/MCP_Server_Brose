# 🎯 MCP服务器端口配置快速指南

## 🚀 三种简单的端口配置方法

### **方法1：编辑 .env 文件（推荐）**

#### 步骤：
1. 打开 `.env` 文件
2. 修改 `MCP_PORT=8000` 为你想要的端口
3. 保存文件
4. 正常启动：`python main.py`

#### 示例：
```bash
# 编辑配置文件
vim .env

# 修改端口
MCP_PORT=9000

# 保存并启动
python main.py
```

---

### **方法2：使用交互式脚本**

#### 步骤：
1. 运行配置脚本
2. 选择修改端口选项
3. 输入新端口号
4. 脚本自动更新配置

#### 示例：
```bash
./change_port.sh

# 输出：
# 🔧 MCP服务器端口配置工具
# 请选择操作:
# 1. 修改端口        # ← 选择这个
# 2. 查看当前配置
# 3. 编辑.env文件
# 4. 恢复默认配置
```

---

### **方法3：命令行快速修改**

#### 步骤：
1. 使用sed命令直接修改
2. 验证修改结果
3. 启动服务器

#### 示例：
```bash
# 修改端口为9000
sed -i.bak 's/MCP_PORT=.*/MCP_PORT=9000/' .env

# 验证修改
grep MCP_PORT .env

# 启动服务器
python main.py
```

---

## 📋 .env 文件详解

### **当前配置结构**
```bash
# MCP服务器环境配置文件

# 🔧 服务器配置 - 修改这里来改变端口！
MCP_HOST=0.0.0.0        # 监听地址 (0.0.0.0 = 所有网络接口)
MCP_PORT=8000           # 端口号 (修改这个！)

# 🐛 调试模式
MCP_DEBUG=false         # 是否启用调试模式

# 📋 日志配置
LOG_LEVEL=INFO          # 日志级别 (DEBUG, INFO, WARNING, ERROR)
LOG_FILE=mcp_server.log # 日志文件名

# ⏱️ 请求配置
REQUEST_TIMEOUT=30      # 请求超时时间(秒)

# 🔒 SSL配置
SSL_VERIFY=false        # 是否验证SSL证书
```

---

## 🎯 不同环境的配置建议

### **开发环境**
```bash
MCP_HOST=127.0.0.1      # 仅本地访问
MCP_PORT=8000
MCP_DEBUG=true
LOG_LEVEL=DEBUG
```

### **测试环境**
```bash
MCP_HOST=0.0.0.0
MCP_PORT=8001
MCP_DEBUG=false
LOG_LEVEL=INFO
```

### **生产环境**
```bash
MCP_HOST=0.0.0.0
MCP_PORT=80            # 标准HTTP端口
MCP_DEBUG=false
LOG_LEVEL=WARNING
```

---

## 🔧 配置管理最佳实践

### **✅ 推荐做法**

1. **使用 .env 文件**
   ```bash
   # 集中管理所有配置
   # 便于版本控制
   # 支持不同环境
   ```

2. **创建环境特定配置**
   ```bash
   .env.development     # 开发环境
   .env.testing         # 测试环境
   .env.production     # 生产环境
   ```

3. **备份配置文件**
   ```bash
   cp .env .env.backup
   ```

### **❌ 避免的做法**

1. **硬编码端口**
   ```python
   # 不好
   PORT: int = 8000
   
   # 好
   PORT: int = int(os.getenv("MCP_PORT", "8000"))
   ```

2. **在多个地方配置**
   ```bash
   # 不好：配置分散
   # 在settings.py中配置
   # 在.env中配置
   # 在命令行中配置
   
   # 好：统一在.env中管理
   ```

---

## 🚀 快速开始

### **1. 首次配置**
```bash
# .env文件已自动创建，直接编辑即可
vim .env
```

### **2. 修改端口**
```bash
# 方法A: 使用脚本
./change_port.sh

# 方法B: 直接编辑
vim .env  # 修改MCP_PORT=9000

# 方法C: 命令行
sed -i.bak 's/MCP_PORT=.*/MCP_PORT=9000/' .env
```

### **3. 验证配置**
```bash
# 查看当前配置
cat .env

# 或查看端口配置
grep MCP_PORT .env
```

### **4. 启动服务器**
```bash
# 配置会自动加载
python main.py

# 或使用启动脚本
./start.sh
```

---

## 🔍 故障排除

### **问题1：配置不生效**
```bash
# 检查.env文件是否存在
ls -la .env

# 检查文件权限
chmod 644 .env

# 重启服务器
python main.py
```

### **问题2：端口冲突**
```bash
# 检查端口占用
lsof -i :8000

# 更换端口
./change_port.sh
# 选择不同端口
```

### **问题3：需要恢复默认配置**
```bash
# 恢复默认配置
cp .env.example .env

# 或使用脚本
./change_port.sh
# 选择"恢复默认配置"
```

---

## 📊 配置优先级

配置的优先级从高到低：

1. **环境变量** (最高)
   ```bash
   MCP_PORT=9000 python main.py
   ```

2. **.env 文件** (推荐)
   ```bash
   # .env文件中的配置
   MCP_PORT=8000
   ```

3. **config/settings.py默认值** (最低)
   ```python
   PORT: int = int(os.getenv("MCP_PORT", "8000"))
   ```

---

## 💡 使用技巧

### **快速切换环境**
```bash
# 开发环境
cp .env.development .env
python main.py

# 生产环境
cp .env.production .env
python main.py
```

### **临时使用不同端口**
```bash
# 不修改配置文件，临时使用其他端口
MCP_PORT=9000 python main.py
```

### **查看配置是否生效**
```bash
# 启动后查看日志
tail -f logs/mcp_server.log

# 查找端口信息
grep "port" logs/mcp_server.log
```

---

## 📝 总结

**🎯 推荐配置方式：**

1. **日常使用** → 编辑 `.env` 文件
2. **快速切换** → 使用 `./change_port.sh` 脚本
3. **临时修改** → 环境变量 `MCP_PORT=9000 python main.py`

**记住：** `.env` 文件是你的主要配置文件，修改后重启服务器即可生效！
