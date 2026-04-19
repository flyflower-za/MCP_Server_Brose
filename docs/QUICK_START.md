# 🚀 MCP服务器快速配置指南

## 🎯 端口配置（唯一方法）

### **修改端口**
```bash
# 1. 编辑 .env 文件
vim .env

# 2. 修改这一行
MCP_PORT=8000  # 改成你想要的端口

# 3. 保存并启动
python main.py
```

### **验证配置**
```bash
# 查看当前配置
cat .env | grep MCP_PORT

# 检查服务器状态
./check_startup.sh
```

---

## 📋 完整配置示例

### **开发环境 (.env)**
```bash
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_DEBUG=false
LOG_LEVEL=INFO
```

### **生产环境**
```bash
MCP_HOST=0.0.0.0
MCP_PORT=80
MCP_DEBUG=false
LOG_LEVEL=WARNING
```

---

## 🔧 常用命令

### **启动服务器**
```bash
python main.py
```

### **检查状态**
```bash
./check_startup.sh
```

### **查看日志**
```bash
tail -f logs/mcp_server.log
```

---

## 📖 详细文档

查看 [docs/README.md](docs/README.md) 获取完整文档。
