# 变更日志 (CHANGELOG)

本文档记录 MCP Servers Hub 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [Unreleased]

### 🎯 计划中
- Docker 支持
- 自动恢复机制
- 日志聚合系统
- 插件系统

---

## [1.0.3] - 2026-04-28

### ✨ 新增功能

#### **Dashboard统一测试中心** ⭐⭐⭐
- ✅ 配置驱动的测试面板架构，解决扩展性问题
- ✅ 选项卡界面设计，支持无限MCP服务器扩展
- ✅ 智能接口选择，自动选择最优API端点
- ✅ 统一的结果显示和错误处理机制
- ✅ 动态表单生成，支持多种输入类型

#### **二维码扫描器专用API接口** ⭐⭐⭐
- ✅ 新增URL专用接口：`POST /qrcode/qrreader/url`
- ✅ 新增Base64专用接口：`POST /qrcode/qrreader/base64`
- ✅ 保留通用接口向后兼容：`POST /qrcode/qrreader`
- ✅ API语义更清晰，请求体更简洁

#### **Dashboard认证开关配置** ⭐⭐
- ✅ 新增`DASHBOARD_AUTH_ENABLED`环境变量配置
- ✅ 支持启用/禁用密码认证模式
- ✅ 系统API返回认证配置状态
- ✅ Dashboard智能初始化流程

### 🔧 改进优化

#### **启动脚本端口管理** ⭐⭐⭐
- ✅ 扩展端口清理范围：51234-51244
- ✅ 自动清理所有相关MCP服务器进程
- ✅ 解决端口冲突导致的启动失败问题
- ✅ 提供详细的清理日志反馈

#### **API路径命名优化** ⭐⭐⭐
- ✅ 二维码API重命名：`/read` → `/qrreader`
- ✅ 更直观的API路径命名规范
- ✅ Dashboard显示完整API端点列表
- ✅ 新增接口描述和使用提示

#### **Dashboard健壮性提升** ⭐⭐
- ✅ 修复DOM元素null访问错误
- ✅ 添加全面的元素存在性检查
- ✅ 优化认证流程的错误处理
- ✅ 改进登录/登出逻辑

#### **用户体验优化** ⭐⭐
- ✅ API端点卡片显示功能描述
- ✅ 推荐接口用⭐标记
- ✅ 优化输入框提示信息
- ✅ 改进复制地址功能

### 🐛 Bug修复

#### **关键问题修复** ⭐⭐⭐
- ✅ 修复Dashboard无法加载状态的DOM访问错误
- ✅ 解决JavaScript语法错误（多余的大括号）
- ✅ 修复认证禁用时的初始化问题
- ✅ 解决端口冲突导致的MCP服务器启动失败

### 📝 文档更新

#### **新增文档**
- ✅ `docs/QR_API_IMPROVEMENTS.md` - 二维码API改进详解
- ✅ `docs/DASHBOARD_API_UPDATE.md` - Dashboard更新说明
- ✅ `docs/DASHBOARD_IMPROVEMENTS.md` - Dashboard优化建议
- ✅ `docs/DASHBOARD_SCALABLE_DESIGN.md` - 可扩展架构设计

#### **更新文档**
- ✅ `CHANGELOG.md` - 完整记录所有变更
- ✅ `docs/MCP_SERVER_DEVELOPMENT.md` - MCP服务器开发指南
- ✅ `docs/QR_CODE_READER.md` - 二维码识别器文档

### 🔄 迁移指南

#### **从1.0.2升级到1.0.3**

**无破坏性变更**:
- 所有旧API路径仍然可用
- Dashboard向后兼容
- 现有配置无需修改

**建议采用的改进**:
1. 使用新的专用API接口（URL和Base64）
2. 启用Dashboard统一测试中心
3. 配置认证开关根据需求调整
4. 使用更新后的启动脚本

**可选优化**:
```bash
# 建议更新的配置项
DASHBOARD_AUTH_ENABLED=true/false  # 根据需求设置
DASHBOARD_PASSWORD=your_secure_password  # 修改默认密码
```

---

## [1.0.2] - 2026-04-27

### ✨ 新增功能

#### **QR Code Reader MCP Server** ⭐⭐⭐
- ✅ 全新的二维码识别服务
- ✅ 支持多种输入方式：
  - 图片 URL 识别
  - Base64 图片数据识别
  - 文本形式二维码内容处理
- ✅ 批量二维码识别支持
- ✅ 返回二维码位置和元数据信息
- ✅ 基于 OpenCV 的高性能识别
- ✅ 完整的错误处理和日志记录

**新增文件**:
- `mcp_servers/qrcode_reader/__init__.py` - 模块初始化
- `mcp_servers/qrcode_reader/server.py` - 服务实现和路由
- `mcp_servers/qrcode_reader/models.py` - 数据模型定义

**新增 API**:
- `POST /qrcode/read` - 识别单个二维码
- `POST /qrcode/read/batch` - 批量识别二维码
- `GET /qrcode/health` - 健康检查

**新增文档**:
- `docs/QR_CODE_READER.md` - 二维码识别器完整使用指南

#### **Dashboard 二维码测试面板** ⭐⭐
- ✅ 侧边栏新增二维码识别测试面板
- ✅ 支持图片 URL 输入
- ✅ 支持 Base64 数据输入
- ✅ 实时显示识别结果
- ✅ 在线/离线状态显示

**修改文件**:
- `dashboard/index.html` - 添加二维码测试面板和 API 端点显示

### 📝 文档更新

#### **文档结构优化** ⭐⭐⭐
- ✅ **文档清理**: 从 29 个文档精简到 15 个
- ✅ **文档整合**: 从 15 个文档优化到 10 个
- ✅ 删除临时性检查报告和过时文档
- ✅ 合并重复内容，提高文档质量

**删除的文档** (13个):
- 临时检查报告: `BUTTON_FUNCTION_CHECK.md`, `FIX_SUMMARY.md`, `PROJECT_STATUS.md`, `PROJECT_CLEANUP_SUMMARY.md`
- 过时文档: `CHANGELOG_2026_04_21.md`, `DASHBOARD_FEATURES_COMPLETED.md`, `DASHBOARD_THEME_UPDATE.md`, `IMPROVEMENT_RECOMMENDATIONS.md`
- 重复文档: `PROJECT_ANALYSIS_REPORT.md`, `DOCS_STRUCTURE_SUMMARY.md`, `FILE_ORGANIZATION.md`
- 过时指南: `SCRIPTS_FINAL_GUIDE.md`, `SCRIPT_USAGE.md`
- 其他: `client_example.md`

**新增文档** (3个):
- `docs/GETTING_STARTED.md` - 综合快速开始指南（整合了 START_HERE.md + QUICK_START.md + STARTUP_GUIDE.md）
- `docs/PORT_GUIDE.md` - 完整端口管理指南（整合了 PORT_CONFIG_GUIDE.md + PORT_MANAGEMENT.md）
- `docs/PROJECT_OVERVIEW.md` - 项目综合概述（整合了 PROJECT_ANALYSIS.md + PROJECT_STRUCTURE.md）

**删除的文档** (7个):
- `START_HERE.md`, `QUICK_START.md`, `STARTUP_GUIDE.md`
- `PORT_CONFIG_GUIDE.md`, `PORT_MANAGEMENT.md`
- `PROJECT_ANALYSIS.md`, `PROJECT_STRUCTURE.md`

**文档优化效果**:
- 数量减少: 29 → 15 → 10 (减少 66%)
- 内容更全面: 整合后的文档内容更加完整
- 结构更清晰: 相关内容集中，减少查找时间
- 维护更简单: 减少了文档数量，降低维护成本

### 🔧 改进

#### **Dashboard 功能增强**
- ✅ 更新 API 端点生成逻辑，支持新的 qrcode_reader 服务
- ✅ 优化二维码识别服务状态显示
- ✅ 添加二维码测试面板到默认展开列表
- ✅ 改进服务器卡片中 API 端点的显示

#### **代码质量提升**
- ✅ 统一 MCP 服务器模块结构
- ✅ 改进错误处理和日志记录
- ✅ 优化代码注释和文档字符串

### 📦 依赖更新

**新增依赖**:
```
opencv-python>=4.8.0    # 计算机视觉库，用于二维码检测
qrcode>=7.4.0           # 二维码生成和识别库
```

**移除依赖**:
```
pyzbar>=0.1.9           # 不再需要 zbar 库依赖
```

**原因**: 
- OpenCV 是更通用的计算机视觉库
- 避免系统依赖（pyzbar 需要 zbar shared library）
- 更好的跨平台兼容性

### 🧪 测试

#### **新增测试**
- ✅ 二维码识别功能测试（文本输入、Base64 图片）
- ✅ 批量识别测试
- ✅ 错误处理测试
- ✅ Dashboard 集成测试

**测试结果**: 所有测试通过 ✅

### 🎨 UI/UX 改进

#### **Dashboard 新增组件**
- ✅ 二维码识别测试面板
- ✅ 二维码服务状态徽章
- ✅ API 端点动态显示（支持二维码服务）

#### **交互优化**
- ✅ 更直观的测试界面
- ✅ 实时状态更新
- ✅ 更好的错误提示

### 📊 文件变更统计

**新增文件**: 7 个
- `mcp_servers/qrcode_reader/` 目录 (3个文件)
- `docs/` 目录 (3个新文档，7个删除)
- `test_qrcode_complete.py` (测试文件，已清理)

**修改文件**: 4 个
- `config/settings.py` - 注册新服务器
- `requirements.txt` - 更新依赖
- `dashboard/index.html` - 添加二维码测试面板
- `CHANGELOG.md` - 本文件

**删除文件**: 20 个
- 文档清理: 13 个过时文档
- 文档整合: 7 个被合并的文档

### 🔄 兼容性

#### **向后兼容**
- ✅ 所有现有 API 保持不变
- ✅ 新增服务不影响现有服务
- ✅ 配置文件格式兼容
- ✅ Dashboard 界面兼容

#### **迁移指南**
- ✅ 无需迁移，直接使用
- ✅ 新服务自动启用（enabled: true）
- ✅ 文档自动更新

### 💡 使用建议

#### **新用户**
1. 阅读全新的 `docs/GETTING_STARTED.md` 快速开始
2. 在 Dashboard 中测试二维码识别功能
3. 查看 `docs/QR_CODE_READER.md` 了解详细用法

#### **现有用户**
1. 重启系统以启用新的二维码服务
2. 查看 Dashboard 中的新测试面板
3. 更新书签到新的文档结构

### 🔮 未来计划

#### **下一版本** (1.1.0)
- 📋 更多 MCP 服务器集成
- 📊 性能监控面板增强
- 🔔 告警系统
- 🐳 Docker 容器化支持
- 🔄 CI/CD 流水线

---

## [1.0.1] - 2026-04-22

### ✨ 新增功能

#### **PM2 进程管理集成** ⭐⭐⭐
- ✅ PM2 配置文件 `ecosystem.config.js`
- ✅ 全局管理命令 `mcp-server`
- ✅ 自动重启支持
- ✅ 开机自启动支持

**使用方式**:

**方式 1：全局命令（推荐）**
```bash
mcp-server start    # 启动
mcp-server stop     # 停止
mcp-server restart  # 重启
mcp-server status   # 状态
mcp-server logs     # 日志
```

**方式 2：PM2 原生命令**
```bash
# 首次启动
pm2 start ecosystem.config.js

# 后续管理
pm2 restart mcp-server
pm2 stop mcp-server
pm2 status mcp-server
pm2 logs mcp-server
```

**开机自启动**
```bash
pm2 save
pm2 startup
```

#### **启动脚本优化**
- ✅ 优化 `start_safe.sh` 启动脚本
  - 集成自动停止功能（启动前清理旧进程）
  - 保持 `stop.sh` 独立可用

**工作流程**:
```
启动 start_safe.sh
    ↓
检查并调用 stop.sh（清理旧进程）
    ↓
清理完成
    ↓
激活虚拟环境
    ↓
启动服务器
```

### ⚙️ 配置优化

#### **端口自动跟随**
- ✅ `PROCESS_BASE_PORT` 现在自动设置为 `MCP_PORT + 1`
```bash
# .env 配置
MCP_PORT=51234
# PROCESS_BASE_PORT 自动设置为 51235
```

#### **超时时间优化**
- ✅ 默认超时：30 秒 → **120 秒**
- ✅ 中间件超时现在从配置文件读取
- ✅ 解决大 PDF 处理时的超时问题

#### **环境配置文件**
- ✅ `.env` - 实际使用的配置
- ✅ `config.env` - 配置模板
- ✅ 新增进程管理配置项

**完整配置示例**:
```bash
# 服务器配置
MCP_HOST=0.0.0.0
MCP_PORT=51234

# 请求超时（默认 120 秒）
REQUEST_TIMEOUT=120

# 进程管理
PROCESS_BASE_PORT=51235  # 自动跟随 MCP_PORT + 1
PROCESS_MAX_RESTART=3
PROCESS_HEALTH_CHECK_INTERVAL=30
PROCESS_AUTO_RESTART=true
```

### 🐛 Bug 修复
- ✅ 修复 `api/config.py` 语法错误（删除重复代码块）
- ✅ 修复 n8n 集成文档中错误的端点路径（`/extract` → `/pdf/extract`）
- ✅ 修复请求超时配置（从硬编码 30 秒改为配置文件读取）

**语法错误详情**:
- **文件**: `api/config.py`
- **问题**: 重复代码块导致语法错误
- **修复**: 删除重复的函数定义

**端点路径错误详情**:
- **文件**: `docs/N8N_INTEGRATION.md`
- **问题**: 错误的端点路径 `/extract`
- **修复**: 更正为 `/pdf/extract`

**超时配置详情**:
- **文件**: `middleware/proxy_middleware.py`
- **问题**: 硬编码 30 秒超时
- **修复**: 从 `REQUEST_TIMEOUT` 配置读取

### 📝 文档更新
- ✅ 修复 `docs/N8N_INTEGRATION.md` 中的端点路径错误
- ✅ 更新配置说明，明确端口跟随机制

### 🔧 改进
- ✅ 中间件超时时间现在从配置文件读取（`REQUEST_TIMEOUT`）
- ✅ 配置文件 `config.env` 作为模板，`.env` 为实际使用

### 📦 新增文件
- `ecosystem.config.js` - PM2 配置文件
- `/usr/local/bin/mcp-server` - 全局管理命令

### 🔄 修改文件
- `config/settings.py` - 进程端口跟随机制、超时配置
- `middleware/proxy_middleware.py` - 使用配置的超时时间
- `api/config.py` - 修复语法错误
- `.env` - 新增进程管理配置
- `config.env` - 新增进程管理配置
- `docs/N8N_INTEGRATION.md` - 修复端点路径

### 🔄 升级指南

#### **从旧版本升级**

1. **更新代码**
   ```bash
   git pull origin main
   ```

2. **创建 .env 文件**
   ```bash
   cp config.env .env
   ```

3. **停止旧进程**
   ```bash
   bash stop.sh
   ```

4. **使用 PM2 启动**
   ```bash
   mcp-server start
   ```

5. **保存 PM2 配置**
   ```bash
   pm2 save
   pm2 startup
   ```

### 💡 使用建议

#### **环境选择**
1. **生产环境推荐使用 PM2**
   - 自动重启
   - 开机自启
   - 日志管理

2. **开发环境可使用传统方式**
   ```bash
   bash start_safe.sh  # 前台运行，查看实时日志
   ```

#### **配置管理**
- 修改 `.env` 后需要重启
  ```bash
  mcp-server restart
  ```

### 🐛 已知问题
无

---

## [1.0.0] - 2026-04-22

### ✨ 新增功能

#### **配置持久化系统** ⭐⭐⭐
- ✅ 配置自动保存到磁盘
- ✅ 启动时自动加载配置
- ✅ 配置备份（保留最近 10 个）
- ✅ 配置导入/导出功能
- ✅ 配置状态查询 API

**新增文件**:
- `utils/config_manager.py` - 配置管理器
- `config/servers.json.example` - 服务器配置示例
- `config/ports.json.example` - 端口配置示例
- `config/settings.json.example` - 系统设置示例
- `config/.gitignore` - Git 忽略规则

**新增 API**:
- `GET /api/v1/config/status` - 查看配置状态
- `POST /api/v1/config/save` - 手动保存配置
- `POST /api/v1/config/import` - 重载配置文件

**修改文件**:
- `config/port_config.py` - 使用 ConfigManager
- `api/config.py` - 自动保存配置

#### **JWT Token 认证** ⭐⭐⭐
- ✅ JWT Token 登录界面
- ✅ Token 自动存储（localStorage）
- ✅ "记住我" 功能（7 天免登录）
- ✅ Token 过期自动跳转登录
- ✅ 密码哈希存储（HMAC-SHA256）
- ✅ 混合验证（JWT + Basic Auth）

**新增文件**:
- `utils/security.py` - 安全工具（JWT、密码哈希）
- `utils/auth.py` - 认证 API

**新增 API**:
- `POST /api/v1/auth/login` - 登录获取 Token
- `POST /api/v1/auth/verify-token` - 验证 Token
- `POST /api/v1/auth/change-password` - 修改密码

#### **性能监控面板** ⭐⭐⭐
- ✅ Hub CPU 使用率监控
- ✅ Hub 内存使用监控
- ✅ 端口池状态（已用/总数）
- ✅ 运行进程数监控
- ✅ 自动刷新（每 5 秒）

**新增 API**:
- `GET /api/v1/system/resources` - 系统资源监控

**新增文件**:
- `api/system.py` - 系统监控 API

#### **搜索和过滤** ⭐⭐
- ✅ 实时文本搜索（名称、模块、描述、ID）
- ✅ 状态过滤（全部/运行中/已停止）
- ✅ 前端实时过滤，无需后端支持

#### **配置管理界面** ⭐⭐⭐
- ✅ 可视化添加服务器
- ✅ 可视化编辑服务器配置
- ✅ 启用/禁用服务器
- ✅ 删除服务器
- ✅ 自动保存配置到磁盘

**新增 API**:
- `GET /api/v1/config/servers` - 查看所有服务器配置
- `POST /api/v1/config/servers?id={id}` - 添加服务器
- `PUT /api/v1/config/servers/{id}` - 更新服务器
- `DELETE /api/v1/config/servers/{id}` - 删除服务器
- `PATCH /api/v1/config/servers/{id}/toggle?enabled={bool}` - 启用/禁用

#### **版本信息和导出** ⭐⭐
- ✅ 显示当前版本号
- ✅ 一键导出配置（JSON 文件）
- ✅ 导出文件命名：`mcp-hub-config-YYYY-MM-DD.json`

#### **根路径重定向** ⭐
- ✅ 访问 `/` 自动重定向到 `/dashboard`
- ✅ 新增系统信息 API：`GET /api/v1/system`

### 🔧 改进

#### **API 权限调整**
**移除认证**（开放工作流调用）:
- ✅ 所有服务器管理 API（`/api/v1/servers/*`）
- ✅ 所有端口配置 API（`/api/v1/servers/port-configs`）
- ✅ 所有系统监控 API（`/api/v1/system/*`）
- ✅ 健康检查 API（`/health`）

**保留认证**（管理功能）:
- ✅ Dashboard 页面（`/dashboard`）
- ✅ 配置管理 API（`/api/v1/config/*`）
- ✅ 认证 API（`/api/v1/auth/*`）

**原因**: 方便 n8n 等工作流工具直接调用，无需配置认证。

#### **Dashboard 优化**
- ✅ 添加搜索和过滤功能
- ✅ 添加性能监控面板
- ✅ 添加配置管理面板
- ✅ 添加版本信息显示
- ✅ 添加导出配置按钮
- ✅ 优化登录流程（Token 存储）
- ✅ 添加用户信息显示和退出按钮

#### **代理中间件优化**
- ✅ 更新跳过路径列表
- ✅ 添加 `/api/v1/auth` 跳过
- ✅ 添加 `/api/v1/config` 跳过
- ✅ 添加 `/api/v1/system` 跳过

### 🐛 修复

#### **循环导入问题**
- ✅ 修复 `utils/config_manager.py` 的循环导入
- ✅ 改用标准 `logging` 模块

#### **认证逻辑问题**
- ✅ 修复混合验证函数的依赖注入问题
- ✅ 手动解析 Authorization 头
- ✅ JWT Token 优先于 Basic Auth

#### **API 导入错误**
- ✅ 修复 `api/config.py` 缺少 `hmac` 导入
- ✅ 修复 `api/config.py` 使用不存在的 `verify_auth`
- ✅ 统一使用 `verify_basic_auth`

### 📝 文档更新

#### **新增文档**
- ✅ `docs/CONFIG_PERSISTENCE.md` - 配置持久化完整指南
- ✅ `DASHBOARD_FEATURES_COMPLETED.md` - Dashboard 功能完成报告
- ✅ `CHANGELOG.md` - 变更日志（本文件）

#### **更新文档**
- ✅ `README.md` - 全面重写，反映所有新功能
- ✅ `.gitignore` - 添加配置文件忽略规则

### 📊 测试

#### **新增测试**
- ✅ `test_config_persistence.py` - 配置管理器测试
- ✅ `tests/test_process_manager.py` - 进程管理器测试
- ✅ `tests/test_port_allocator.py` - 端口分配器测试

**测试覆盖率**: ~25%

### 🔒 安全

#### **新增安全特性**
- ✅ JWT Token 认证
- ✅ 密码哈希存储（HMAC-SHA256）
- ✅ 时序安全的密码比较
- ✅ Token 过期机制（24 小时）
- ✅ CORS 可配置

#### **安全改进**
- ✅ 移除明文密码存储
- ✅ 支持密码强度验证
- ✅ 可配置 JWT 密钥

### 📦 依赖更新

**新增依赖**:
```
PyJWT>=2.8.0  # JWT Token 支持
```

### 🎨 UI/UX 改进

#### **Dashboard 新增组件**
- ✅ 登录模态框
- ✅ 配置管理面板
- ✅ 性能监控面板
- ✅ 搜索和过滤栏
- ✅ 版本信息显示
- ✅ 导出配置按钮
- ✅ 用户信息显示

#### **交互优化**
- ✅ 实时搜索（无需点击搜索按钮）
- ✅ 状态过滤（下拉选择）
- ✅ 自动保存配置
- ✅ Toast 通知优化

### 🚀 性能优化

- ✅ 性能监控每 5 秒自动刷新
- ✅ 配置变更自动保存（避免手动操作）
- ✅ 日志自动轮转（防止单文件过大）

### 🔄 兼容性

#### **向后兼容**
- ✅ 保留 Basic Auth 支持
- ✅ 保留原有 API 端点
- ✅ 配置文件格式不变

#### **迁移指南**
- ✅ 旧配置可直接使用
- ✅ 新增 `.example` 配置文件
- ✅ 自动创建配置目录

---

## [0.9.0] - 2026-04-21

### ✨ 新增功能
- 进程隔离架构
- 动态端口分配
- 固定端口配置
- Dashboard 白色主题
- 基础服务器管理

### 📝 已知问题
- 配置不持久化（重启丢失）
- 无性能监控
- 无配置管理界面
- Basic Auth 认证（用户体验差）

---

## 版本说明

### **版本号格式**
- **Major.Minor.Patch** (主版本.次版本.补丁版本)
- 示例：`1.0.0`

### **变更类型**
- ✨ **新增功能** - 新特性
- 🔧 **改进** - 现有功能增强
- 🐛 **修复** - Bug 修复
- 📝 **文档** - 文档更新
- 🔒 **安全** - 安全相关
- 📦 **依赖** - 依赖变更
- 🎨 **UI/UX** - 界面优化
- 🚀 **性能** - 性能优化
- 🔄 **兼容性** - 兼容性相关
- ❌ **移除** - 移除功能

---

**最后更新**: 2026-04-27  
**维护者**: Jimmy
