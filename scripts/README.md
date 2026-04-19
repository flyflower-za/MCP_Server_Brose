# 📜 脚本目录使用指南

## 🚀 快速开始

所有脚本已从根目录移动到 `scripts/` 目录，使用时脚本会自动跳转到项目根目录。

---

## 📂 脚本分类

### **🔧 主服务脚本**

#### `scripts/start.sh`
**用途:** 标准启动MCP服务器
```bash
./scripts/start.sh
# 或
bash scripts/start.sh
```

#### `scripts/start_safe.sh`
**用途:** 安全启动（自动清理端口冲突）
```bash
./scripts/start_safe.sh
```

#### `scripts/restart.sh`
**用途:** 重启MCP服务器
```bash
./scripts/restart.sh
```

#### `scripts/check_startup.sh`
**用途:** 检查服务器状态（支持动态端口）
```bash
./scripts/check_startup.sh
```

### **🛠️ 开发工具脚本**

#### `scripts/create_mcp_server.py`
**用途:** 创建新的MCP服务器模块
```bash
python scripts/create_mcp_server.py my_service "服务描述"
```

#### `scripts/port_manager.sh`
**用途:** 交互式端口管理（可选）
```bash
./scripts/port_manager.sh
```

### **🔍 测试工具脚本**

#### `scripts/utils/test_n8n_api.py`
**用途:** 测试n8n API调用
```bash
python scripts/utils/test_n8n_api.py
```

#### `scripts/utils/test_n8n_connection.sh`
**用途:** 检查n8n连接配置
```bash
./scripts/utils/test_n8n_connection.sh
```

---

## 🎯 使用方法

### **方法1: 相对路径调用（推荐）**
```bash
# 从项目根目录调用
./scripts/start.sh
./scripts/check_startup.sh
```

### **方法2: 绝对路径调用**
```bash
# 从任何位置调用
bash /path/to/MCP_Server/scripts/start.sh
```

### **方法3: 进入scripts目录**
```bash
cd scripts
./start.sh        # 会自动跳转到项目根目录
./check_startup.sh
```

---

## 💡 重要特性

所有主脚本都包含路径跳转逻辑：
```bash
# 进入项目根目录
cd "$(dirname "$0")/.."
```

这确保脚本无论从哪里被调用都能正常工作。

---

## 🔄 日常使用

### **启动服务器**
```bash
# 最简单的方式
./scripts/start.sh

# 或安全启动
./scripts/start_safe.sh
```

### **检查状态**
```bash
./scripts/check_startup.sh
```

### **重启服务器**
```bash
./scripts/restart.sh
```

### **创建新服务**
```bash
python scripts/create_mcp_server.py my_service
```

---

## 📋 脚本功能对比

| 脚本 | 用途 | 适用场景 |
|------|------|----------|
| **start.sh** | 标准启动 | 日常使用 |
| **start_safe.sh** | 安全启动 | 有端口冲突时 |
| **restart.sh** | 重启服务 | 更新代码后 |
| **check_startup.sh** | 状态检查 | 验证运行状态 |
| **create_mcp_server.py** | 创建服务 | 开发新功能 |

---

## 🛠️ 故障排除

### **问题1: 脚本执行权限**
```bash
# 如果遇到权限错误
chmod +x scripts/*.sh
chmod +x scripts/utils/*.sh
```

### **问题2: 脚本找不到文件**
```bash
# 确认脚本中的路径跳转生效
head -5 scripts/start.sh | grep "cd.*dirname"
```

### **问题3: 端口冲突**
```bash
# 使用安全启动脚本
./scripts/start_safe.sh
```

---

## 🎉 整理效果

### **✅ 根目录更清爽**
- 整理前: 6个脚本文件混杂
- 整理后: 只有核心业务文件

### **✅ 脚本分类清晰**
- 主服务脚本: `scripts/`
- 工具脚本: `scripts/utils/`

### **✅ 维护更方便**
- 所有脚本集中管理
- 统一的路径处理
- 清晰的功能分类

---

## 💡 最佳实践

1. **使用相对路径** - `./scripts/start.sh`
2. **脚本自动定位** - 无需手动cd
3. **功能明确分类** - 按用途选择脚本
4. **保持简洁** - 根目录只保留核心文件

---

**🎯 现在根目录非常清爽，所有脚本都在scripts/目录中！**
