# 🚀 脚本使用快速指南

## 📂 新的脚本结构

所有脚本已从根目录移动到 `scripts/` 目录，但使用方式保持不变！

---

## 🎯 最常用的命令

### **启动服务器**
```bash
# 标准启动
./scripts/start.sh

# 安全启动（清理端口冲突）
./scripts/start_safe.sh
```

### **检查状态**
```bash
# 检查服务器状态
./scripts/check_startup.sh
```

### **重启服务器**
```bash
# 重启MCP服务器
./scripts/restart.sh
```

---

## 💡 重要特性

### **✅ 脚本会自动跳转到项目根目录**
所有脚本都包含路径跳转逻辑，无论从哪里调用都能正常工作：
```bash
# 在脚本内部
cd "$(dirname "$0")/.."
```

### **✅ 支持多种调用方式**
```bash
# 方法1: 相对路径（推荐）
./scripts/start.sh

# 方法2: bash调用
bash scripts/start.sh

# 方法3: 进入scripts目录
cd scripts && ./start.sh
```

---

## 🛠️ 其他可用脚本

### **开发工具**
```bash
# 创建新的MCP服务器
python scripts/create_mcp_server.py my_service

# 交互式端口管理
./scripts/port_manager.sh
```

### **测试工具**
```bash
# 测试n8n API调用
python scripts/utils/test_n8n_api.py

# 检查n8n连接配置
./scripts/utils/test_n8n_connection.sh
```

---

## 📋 脚本功能一览

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| **scripts/start.sh** | 标准启动 | 日常使用 |
| **scripts/start_safe.sh** | 安全启动 | 端口冲突时 |
| **scripts/restart.sh** | 重启服务 | 更新代码后 |
| **scripts/check_startup.sh** | 状态检查 | 验证运行状态 |
| **scripts/create_mcp_server.py** | 创建服务 | 开发新功能 |
| **scripts/port_manager.sh** | 端口管理 | 修改端口配置 |
| **scripts/utils/test_n8n_api.py** | API测试 | 测试PDF提取 |
| **scripts/utils/test_n8n_connection.sh** | 连接测试 | 检查n8n配置 |

---

## 🔄 从旧版本迁移

### **之前的方式（仍然有效）**
```bash
# 如果你有旧的习惯命令，可以创建别名
alias start='./scripts/start.sh'
alias check='./scripts/check_startup.sh'
alias restart='./scripts/restart.sh'
```

### **新的方式（推荐）**
```bash
# 直接使用相对路径
./scripts/start.sh
./scripts/check_startup.sh
```

---

## 🎯 最佳实践

### **1. 日常开发流程**
```bash
# 1. 启动服务器
./scripts/start.sh

# 2. 检查状态
./scripts/check_startup.sh

# 3. 修改代码后重启
./scripts/restart.sh
```

### **2. 快速测试**
```bash
# 测试服务器状态
./scripts/check_startup.sh

# 测试n8n连接
python scripts/utils/test_n8n_api.py
```

### **3. 开发新功能**
```bash
# 创建新服务
python scripts/create_mcp_server.py new_feature

# 重启服务器
./scripts/restart.sh
```

---

## ✅ 优势

### **项目结构清晰**
- 根目录只保留核心业务文件
- 脚本统一在scripts/目录管理
- 工具脚本分类到utils/子目录

### **使用体验一致**
- 所有脚本支持相同的调用方式
- 脚本自动处理路径问题
- 无需记住复杂的位置

### **维护更加方便**
- 脚本集中管理，容易找到
- 功能分类清晰，用途明确
- 添加新脚本有明确的归属

---

## 📚 相关文档

- **[scripts/README.md](scripts/README.md)** - 脚本详细使用指南
- **[docs/N8N_INTEGRATION.md](docs/N8N_INTEGRATION.md)** - n8n集成指南
- **[docs/QUICK_START.md](docs/QUICK_START.md)** - 快速配置指南

---

**🎯 记住：** 虽然脚本位置变了，但使用方式几乎一样！只需在命令前加上 `scripts/` 前缀即可。
