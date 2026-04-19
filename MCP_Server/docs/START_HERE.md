# 🚀 快速开始指南

## 🎯 最简单的启动方式

### **推荐方法（根目录）**
```bash
./start_safe.sh
```

**功能：** 一键启动，自动处理所有配置问题

---

## 📁 脚本位置

### **根目录**（主要）
- `start_safe.sh` - 主启动脚本 ⭐

### **scripts/ 目录**
- `start.sh` - 标准启动
- `restart.sh` - 重启服务器
- `check_startup.sh` - 状态检查
- `create_mcp_server.py` - 创建新服务
- `port_manager.sh` - 端口管理

### **scripts/utils/ 目录**
- `test_n8n_api.py` - API测试
- `test_n8n_connection.sh` - 连接测试

---

## 💡 使用建议

### **日常使用**
```bash
# 启动服务器（推荐）
./start_safe.sh

# 检查状态
./scripts/check_startup.sh

# 重启服务器
./scripts/restart.sh
```

### **开发工作流**
```bash
# 1. 启动
./start_safe.sh

# 2. 开发测试

# 3. 重启
./scripts/restart.sh

# 4. 检查状态
./scripts/check_startup.sh
```

---

## 🔧 配置管理

### **修改端口**
```bash
# 编辑.env文件
vim .env
# 修改: MCP_PORT=51234
```

### **启动服务器**
```bash
./start_safe.sh
```

---

## 📚 详细文档

- **[docs/QUICK_START.md](docs/QUICK_START.md)** - 快速配置指南
- **[docs/SCRIPT_USAGE.md](docs/SCRIPT_USAGE.md)** - 脚本使用指南
- **[docs/N8N_INTEGRATION.md](docs/N8N_INTEGRATION.md)** - n8n集成指南

---

## 🎯 总结

**最简单的启动方式:**
```bash
./start_safe.sh    # 一键启动，自动处理所有问题
```

**记住:** 根目录的 `start_safe.sh` 是你的主启动脚本！
