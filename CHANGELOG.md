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

**最后更新**: 2026-04-22  
**维护者**: Jimmy
