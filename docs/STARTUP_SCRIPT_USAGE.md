# 🚀 启动脚本使用指南

## 快速开始

### 推荐：使用新的 v2.0 脚本

```bash
# 赋予执行权限（首次使用）
chmod +x start_safe_Mac_v2.sh

# 启动服务器
./start_safe_Mac_v2.sh
```

---

## 📋 v2.0 脚本功能

### 自动检查项

✅ **Python 版本** - 验证 ≥3.8
✅ **虚拟环境** - 自动创建和验证
✅ **依赖完整性** - 检查所有 16+ 个依赖
✅ **配置文件** - 自动创建 .env
✅ **系统资源** - CPU/内存/磁盘检查
✅ **端口状态** - 自动清理占用端口
✅ **日志系统** - 检查日志目录和大小
✅ **服务启动** - 带健康检查验证

---

## 🎨 输出示例

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐍 Python 版本检查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️  当前 Python 版本: 3.12.0
✅ Python 版本符合要求 (≥3.8)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 虚拟环境检查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️  激活虚拟环境...
✅ 虚拟环境已激活: /path/to/.venv

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 依赖检查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️  运行依赖验证脚本...
✅ FastAPI
✅ Uvicorn
✅ OpenCV
...
✅ 所有依赖已正确安装

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 启动信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

服务地址:     http://localhost:51234
API 文档:     http://localhost:51234/docs
Dashboard:    http://localhost:51234/dashboard
健康检查:     http://localhost:51234/health

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏥 健康检查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️  等待服务启动...
✅ API 网关已启动 (端口 51234)
ℹ️  检查健康端点...
✅ 健康检查通过
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  服务器已成功启动并运行在 PID: 12345
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🛠️ 故障排除

### 问题 1: Python 版本过低

```bash
❌ 需要Python 3.8或更高版本
ℹ️  当前版本: 3.7.0

# 解决方案：
# 1. 安装较新的 Python 版本
brew install python@3.12

# 2. 或使用 pyenv 管理多版本
pyenv install 3.12.0
pyenv global 3.12.0
```

### 问题 2: 依赖安装失败

```bash
❌ 依赖检查失败

# 解决方案：
# 1. 手动安装依赖
pip install -r requirements.txt

# 2. 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 3. 查看详细日志
pip install -r requirements.txt -v
```

### 问题 3: 端口清理失败

```bash
⚠️  端口 51234 清理失败，可能需要手动处理

# 解决方案：
# 1. 查看占用端口的进程
lsof -i :51234

# 2. 手动杀死进程
kill -9 <PID>

# 3. 或修改配置使用其他端口
# 编辑 .env 文件
MCP_PORT=51334
```

### 问题 4: 虚拟环境问题

```bash
❌ 虚拟环境激活失败

# 解决方案：
# 1. 删除旧虚拟环境
rm -rf .venv

# 2. 重新创建
python3 -m venv .venv

# 3. 重新安装依赖
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🔧 高级配置

### 自定义端口

编辑 `.env` 文件：
```bash
MCP_PORT=51334  # 修改主端口
```

### 禁用认证

编辑 `.env` 文件：
```bash
DASHBOARD_AUTH_ENABLED=false
```

### 调整日志级别

编辑 `.env` 文件：
```bash
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

---

## 📝 两种脚本对比

### v1.0 (start_safe_Mac.sh)
- ✅ 基础功能
- ⚠️  依赖检查不完整
- ⚠️  无版本验证
- ⚠️  错误处理简单

### v2.0 (start_safe_Mac_v2.sh) - **推荐**
- ✅ 完整的依赖检查
- ✅ Python 版本验证
- ✅ 系统资源监控
- ✅ 启动后健康检查
- ✅ 彩色输出和美化
- ✅ 自动修复常见问题

---

## 💡 使用建议

### 首次使用
```bash
# 1. 使用 v2.0 脚本启动
./start_safe_Mac_v2.sh

# 2. 观察所有检查项
# 3. 确认所有检查通过
# 4. 验证服务正常运行
```

### 日常使用
```bash
# 直接启动（脚本会自动检查）
./start_safe_Mac_v2.sh

# 或使用简短命令
./start_safe_Mac.sh  # 如果已替换为 v2.0
```

### 开发调试
```bash
# 查看详细日志
tail -f logs/mcp_server.log

# 检查服务状态
curl http://localhost:51234/health | python3 -m json.tool

# 查看所有服务
curl http://localhost:51234/api/v1/servers/statuses
```

---

## 🎯 最佳实践

### 1. 启动前检查清单
- [ ] Python 版本 ≥3.8
- [ ] 虚拟环境已激活
- [ ] 依赖已安装
- [ ] 端口未被占用
- [ ] 磁盘空间充足

### 2. 启动后验证
- [ ] 检查健康端点：`curl http://localhost:51234/health`
- [ ] 访问 Dashboard：`open http://localhost:51234/dashboard`
- [ ] 查看 API 文档：`open http://localhost:51234/docs`
- [ ] 检查日志：`tail -f logs/mcp_server.log`

### 3. 停止服务
```bash
# 按 Ctrl+C 优雅停止

# 或手动杀死进程
lsof -ti :51234 | xargs kill -9
```

---

## 📚 相关文档

- [依赖安装指南](DEPENDENCY_INSTALLATION_GUIDE.md)
- [启动脚本对比](STARTUP_SCRIPT_COMPARISON.md)
- [第一阶段完成报告](FINAL_PHASE1_REPORT.md)

---

**最后更新**: 2026-04-28
**推荐版本**: v2.0
**状态**: ✅ 生产就绪
