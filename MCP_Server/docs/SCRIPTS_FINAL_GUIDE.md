# 📜 脚本使用指南

## 🚀 最常用命令（根目录）

### **主启动脚本**
```bash
# 推荐使用（在根目录）
./start_safe.sh    # 安全启动，自动清理端口冲突
```

**功能：**
- ✅ 自动激活虚拟环境
- ✅ 检查并安装依赖
- ✅ 自动清理端口冲突
- ✅ 读取.env中的端口配置
- ✅ 启动MCP服务器

---

## 📁 scripts/ 目录脚本

### **服务管理脚本**
```bash
# 从项目根目录调用
./scripts/start.sh           # 标准启动
./scripts/restart.sh        # 重启服务器
./scripts/check_startup.sh  # 检查状态
```

### **开发工具脚本**
```bash
# 创建新MCP服务器
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

## 💡 使用建议

### **日常开发**
```bash
# 首选：根目录的安全启动
./start_safe.sh
```

### **状态检查**
```bash
# 检查服务器运行状态
./scripts/check_startup.sh
```

### **问题解决**
```bash
# 遇到端口冲突时使用
./start_safe.sh    # 自动清理冲突
```

---

## 📋 完整脚本列表

| 位置 | 脚本 | 用途 |
|------|------|------|
| **根目录** | `start_safe.sh` | 主启动脚本 ⭐ |
| **scripts/** | `start.sh` | 标准启动 |
| **scripts/** | `restart.sh` | 重启服务 |
| **scripts/** | `check_startup.sh` | 状态检查 |
| **scripts/** | `create_mcp_server.py` | 创建服务 |
| **scripts/** | `port_manager.sh` | 端口管理 |
| **scripts/utils/** | `test_n8n_api.py` | API测试 |

---

## 🎯 最佳实践

### **1. 首次启动**
```bash
./start_safe.sh    # 自动处理所有配置
```

### **2. 日常开发**
```bash
./start_safe.sh    # 最方便
```

### **3. 检查状态**
```bash
./scripts/check_startup.sh    # 查看详细状态
```

### **4. 重启服务**
```bash
./scripts/restart.sh    # 快速重启
```

---

## ✅ 优势

### **根目录便捷性**
- ⭐ `start_safe.sh` 在根目录，最常用命令触手可及
- ⭐ 新手友好，不需要记住scripts路径
- ⭐ 符合直觉，启动脚本应该在根目录

### **脚本目录整洁性**
- 📁 其他脚本仍在scripts/中统一管理
- 📁 工具脚本分类在utils/中
- 📁 保持了良好的项目结构

---

## 🔧 工作流程

### **标准启动流程**
```bash
1. ./start_safe.sh     # 启动服务器
2. Ctrl+C             # 停止服务器
3. ./scripts/restart.sh # 重启（如需要）
```

### **开发流程**
```bash
1. ./start_safe.sh                    # 启动
2. 开发/测试代码
3. ./scripts/restart.sh               # 重启
4. ./scripts/check_startup.sh        # 检查状态
```

---

## 💡 总结

**最常用的启动方式:**
```bash
./start_safe.sh    # 一键启动，自动处理所有问题
```

**记住:** 根目录的 `start_safe.sh` 是你的主启动脚本，其他管理脚本在 `scripts/` 目录中！

**🎯 现在项目既保持了便捷性，又保持了整洁性！**
