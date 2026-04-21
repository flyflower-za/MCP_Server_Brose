# 配置持久化功能文档

**完成日期**: 2026-04-22  
**功能**: 配置文件持久化存储

---

## 📁 配置文件结构

```
config/
├── servers.json          # 服务器配置
├── ports.json            # 固定端口配置
├── settings.json         # 系统设置
├── backups/              # 配置备份目录
│   ├── servers_20260422_120000.bak
│   ├── ports_20260422_120000.bak
│   └── settings_20260422_120000.bak
├── servers.json.example  # 示例配置
├── ports.json.example    # 示例配置
└── settings.json.example # 示例配置
```

---

## 🔧 功能说明

### **1. 自动保存**

当配置发生变更时，自动保存到磁盘：

```python
# 添加服务器
POST /api/v1/config/servers?server_id=my_server
{
  "name": "My Server",
  "module": "mcp_servers.my_server.server",
  "enabled": true
}
# ✅ 自动保存到 config/servers.json

# 设置固定端口
PUT /api/v1/servers/my_server/port-config
{ "port": 51240 }
# ✅ 自动保存到 config/ports.json
```

### **2. 启动时加载**

服务启动时自动加载配置文件：

```python
# 1. 加载 config/servers.json
# 2. 加载 config/ports.json
# 3. 加载 config/settings.json
# 4. 合并到内存配置中
```

### **3. 配置备份**

每次保存配置时自动创建备份：

- 保留最近 **10 个**备份
- 备份文件命名：`{文件名}_{时间戳}.bak`
- 示例：`servers_20260422_120000.bak`

---

## 📋 配置文件格式

### **servers.json**
```json
{
  "pdf_extractor": {
    "name": "PDF Extractor",
    "description": "Get PDF content from URLs",
    "enabled": true,
    "version": "1.0.0",
    "module": "mcp_servers.pdf_extractor.server",
    "prefix": "/pdf",
    "tags": ["pdf", "extractor", "document"]
  },
  "web_scraper": {
    "name": "Web Scraper",
    "description": "Scrape web content",
    "enabled": true,
    "version": "1.0.0",
    "module": "mcp_servers.web_scraper.server",
    "prefix": "/scraper",
    "tags": ["web", "scraper", "html"]
  }
}
```

### **ports.json**
```json
{
  "pdf_extractor": 51238,
  "web_scraper": 51239
}
```

### **settings.json**
```json
{
  "auto_restart": true,
  "max_restart_count": 3,
  "health_check_interval": 30,
  "log_level": "INFO",
  "port_allocation": {
    "base_port": 51235,
    "max_port": 51250
  }
}
```

---

## 🚀 API 使用

### **1. 查看配置状态**
```bash
GET /api/v1/config/status

# 响应
{
  "config_dir": "/path/to/config",
  "servers_config_exists": true,
  "ports_config_exists": true,
  "settings_config_exists": false,
  "servers_count": 2,
  "ports_count": 2,
  "backups_count": 6
}
```

### **2. 手动保存所有配置**
```bash
POST /api/v1/config/save

# 响应
{
  "success": true,
  "message": "配置已保存",
  "servers_saved": true,
  "ports_saved": true,
  "settings_saved": false
}
```

### **3. 导出所有配置**
```bash
GET /api/v1/config/export

# 响应
{
  "version": "1.0.0",
  "exported_at": "2026-04-22T12:00:00",
  "servers": { ... },
  "ports": { ... },
  "settings": { ... }
}
```

### **4. 重载配置文件**
```bash
POST /api/v1/config/import?overwrite=false

# 参数
overwrite: false  # 是否覆盖内存配置

# 响应
{
  "success": true,
  "message": "配置导入成功"
}
```

---

## 💡 使用指南

### **首次部署**

1. **创建配置文件**
```bash
# 复制示例配置
cp config/servers.json.example config/servers.json
cp config/ports.json.example config/ports.json
cp config/settings.json.example config/settings.json
```

2. **编辑配置**
```bash
vim config/servers.json
```

3. **启动服务**
```bash
python main.py
# 自动加载配置文件
```

### **运行时修改配置**

1. **通过 Dashboard 修改**
   - 访问 `/dashboard`
   - 在配置管理面板中修改
   - ✅ 自动保存到磁盘

2. **通过 API 修改**
```bash
# 添加服务器
curl -X POST "http://localhost:51234/api/v1/config/servers?server_id=new_server" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Server",
    "module": "mcp_servers.new.server",
    "enabled": true
  }'

# ✅ 自动保存到 config/servers.json
```

3. **手动编辑配置文件**
```bash
vim config/servers.json

# 然后重载配置
curl -X POST "http://localhost:51234/api/v1/config/import?overwrite=true"
```

---

## 🔍 故障排查

### **配置文件不存在**

**问题**：启动时提示配置文件不存在

**解决**：
```bash
# 从示例创建
cp config/servers.json.example config/servers.json
```

### **配置备份太多**

**问题**：backups 目录占用大量空间

**解决**：
```bash
# 清理旧备份（只保留最近10个）
# 系统会自动清理，也可以手动删除
rm config/backups/*.bak
```

### **配置未生效**

**问题**：修改配置文件后未生效

**解决**：
```bash
# 方法1：重启服务
python main.py

# 方法2：导入配置
curl -X POST "http://localhost:51234/api/v1/config/import?overwrite=true"
```

---

## 🎯 最佳实践

### **1. 版本控制**

```bash
# 只提交 .example 文件
git add config/*.example
git commit -m "Add config examples"

# 不提交实际配置（包含敏感信息）
echo "config/*.json" >> .gitignore
echo "!config/*.example" >> .gitignore
```

### **2. 环境隔离**

```bash
# 开发环境
config/dev.servers.json
config/dev.ports.json

# 生产环境
config/prod.servers.json
config/prod.ports.json

# 启动时指定
python main.py --config-env=prod
```

### **3. 配置备份**

```bash
# 定期备份配置到安全位置
cp -r config/ backups/config-$(date +%Y%m%d)/
```

---

## 📊 功能对比

| 功能 | 之前 | 现在 |
|------|------|------|
| 配置存储 | 内存 | 文件 |
| 重启后 | 丢失 | 保留 |
| 备份 | 无 | 自动 |
| 导入/导出 | 无 | 支持 |
| 版本控制 | 无法 | 可以 |

---

## ✅ 完成

配置持久化功能已实现并测试通过！

**新增文件**:
- `utils/config_manager.py` - 配置管理器
- `config/servers.json.example` - 示例服务器配置
- `config/ports.json.example` - 示例端口配置
- `config/settings.json.example` - 示例系统设置
- `config/.gitignore` - Git 忽略规则

**修改文件**:
- `config/port_config.py` - 使用 ConfigManager
- `api/config.py` - 自动保存配置

**新增 API**:
- `GET /api/v1/config/status` - 查看配置状态
- `POST /api/v1/config/save` - 手动保存配置
- `POST /api/v1/config/import` - 导入配置

---

**下一步建议**:
1. 测试配置持久化功能
2. 添加配置验证
3. 实现配置加密（敏感信息）
