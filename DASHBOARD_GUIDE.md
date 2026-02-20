# TrendRadar Dashboard - 使用指南

## 🎯 功能概述

TrendRadar Dashboard 是一个统一的 Web 界面，用于浏览和管理所有 TrendRadar 数据：

- **📊 Dashboard总览** - 实时统计、最新报告预览、最近招标信息
- **📄 报告历史** - 浏览所有历史报告，按时间排序
- **🏢 招标信息** - 搜索和查看招标项目详情
- **📤 推送接收** - 接收Windows客户端推送的数据（API）

---

## 🚀 快速开始

### 1. 启动Dashboard服务

```bash
cd /mnt/oldroot/home/bird/TrendRadar

# 方式1: 使用启动脚本（推荐）
./start_dashboard.sh

# 方式2: 直接启动
python3 -m uvicorn app:app --host 0.0.0.0 --port 8080
```

### 2. 访问Dashboard

浏览器打开：**http://localhost:8080**

你会看到：
- 📊 统计卡片（报告数、招标数、最新时间）
- 📄 最新报告的iframe预览
- 🏢 最近的招标信息列表

---

## 📋 功能详解

### Dashboard总览页

**统计卡片**：
- 总报告数 / 近7天报告数
- 招标信息总数 / 近7天新增
- 最新更新时间

**最新报告预览**：
- 自动加载最新生成的HTML报告
- 支持iframe内查看完整报告内容

**最近招标信息**：
- 显示最近20条招标信息
- 展示标题、来源、金额、发布日期
- 点击标题可跳转到原始网站

### 报告历史页

**功能**：
- 列出所有历史报告文件
- 显示文件名、日期、时间、大小
- 点击可在新标签页打开报告

**排序**：
- 按时间倒序排列（最新在前）

### 招标信息页

**搜索功能**：
- 关键词搜索招标标题
- 实时搜索结果

**信息展示**：
- 招标标题（可点击跳转）
- 来源网站名称
- 预算金额（如有）
- 发布日期（如有）

---

## 🔌 API端点

Dashboard提供以下RESTful API：

### 统计数据
```bash
GET /api/dashboard/stats
```
返回：总报告数、招标数、最新时间等

### 报告列表
```bash
GET /api/dashboard/reports?limit=50&date_from=2026-02-01
```
参数：
- `limit`: 返回数量（默认50）
- `date_from`: 开始日期（可选）
- `date_to`: 结束日期（可选）

### 最新报告
```bash
GET /api/dashboard/reports/latest
```
返回最新生成的HTML报告文件

### 指定报告
```bash
GET /api/dashboard/reports/file?file_path=output/html/2026-02-20/14-01.html
```
返回指定路径的报告文件

### 最近招标
```bash
GET /api/dashboard/tenders/recent?limit=20
```
返回最近的招标信息（JSON格式）

### 搜索招标
```bash
GET /api/dashboard/tenders/search?keyword=软件开发&source=beijing&limit=50
```
参数：
- `keyword`: 搜索关键词（必需）
- `source`: 来源筛选（可选）
- `limit`: 返回数量（默认50）

---

## 🔄 与现有功能的集成

### 1. TrendRadar主程序

Dashboard **不影响** TrendRadar主程序的运行：

```bash
# 运行TrendRadar主程序（生成报告）
python3 run_with_tenders.py

# 报告会自动保存到 output/html/
# Dashboard会自动检测并显示新报告
```

### 2. Windows推送客户端

Windows客户端推送的数据会自动被Dashboard处理：

```cmd
# Windows客户端推送
python windows_tender_collector.py --server http://YOUR_SERVER:8080

# 推送的数据保存到 output/tenders/
# Dashboard会自动加载并显示
```

### 3. 数据同步

Dashboard采用**实时读取**方式：
- 不需要数据库
- 直接读取 `output/` 目录下的文件
- 每次刷新都会加载最新数据

---

## 📁 目录结构

```
TrendRadar/
├── dashboard.html              # Dashboard前端页面
├── start_dashboard.sh          # Dashboard启动脚本
├── app.py                      # FastAPI主应用
├── api/
│   ├── dashboard.py           # Dashboard API路由
│   └── tender_push.py         # Windows推送API
├── output/
│   ├── html/                  # 报告HTML文件
│   │   ├── latest/
│   │   │   └── current.html  # 最新报告
│   │   └── 2026-02-20/
│   │       ├── 14-01.html
│   │       └── 15-35.html
│   └── tenders/               # 招标数据JSON
│       ├── tenders_20260220_140048.json
│       └── tenders_windows_client_20260221_083000.json
└── ...
```

---

## 🎨 界面特性

### 响应式设计
- 支持桌面、平板、手机访问
- 使用 Tailwind CSS 样式框架

### 现代化交互
- Vue.js 3 前端框架
- 无需刷新页面的单页应用
- 流畅的动画和过渡效果

### 实时更新
- 点击"🔄 刷新"按钮加载最新数据
- iframe自动加载最新报告

---

## 🔧 配置和自定义

### 修改端口

编辑 `start_dashboard.sh` 或直接指定：

```bash
python3 -m uvicorn app:app --host 0.0.0.0 --port 9000
```

### 外网访问

如果需要外网访问（如Windows客户端推送）：

1. **开放防火墙端口**：
```bash
# Ubuntu/Debian
sudo ufw allow 8080

# CentOS/RHEL
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload
```

2. **确保监听所有地址**（默认已配置）：
```python
# app.py 中已经设置为 0.0.0.0
host="0.0.0.0"
```

3. **访问地址**：
```
http://YOUR_SERVER_IP:8080
```

---

## 🛡️ 安全建议

### 生产环境

1. **使用反向代理（Nginx/Apache）**：
```nginx
# Nginx配置示例
server {
    listen 80;
    server_name trendradar.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. **添加认证（推荐）**：
```bash
# 使用 HTTP Basic Auth 或 OAuth2
pip install fastapi-security
```

3. **HTTPS配置**：
```bash
# Let's Encrypt 免费证书
sudo certbot --nginx -d trendradar.example.com
```

### 访问控制

如果只在内网使用，可以限制访问IP：

```python
# app.py 添加中间件
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class IPWhitelistMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        allowed_ips = ["127.0.0.1", "192.168.1.0/24"]
        # ... 检查逻辑
        return await call_next(request)
```

---

## 📊 性能和资源

### 资源占用

| 项目 | 数值 |
|-----|------|
| 内存占用 | ~100-150MB |
| CPU占用 | <5%（空闲时） |
| 启动时间 | 1-2秒 |
| 并发支持 | 50+ 连接 |

### 性能优化

1. **启用缓存**（如需要）：
```python
# 添加响应缓存
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

FastAPICache.init(InMemoryBackend())
```

2. **静态文件CDN**（可选）：
- Tailwind CSS、Vue.js 等已使用CDN
- 大型部署可考虑本地化

---

## 🐛 故障排除

### 问题1: 端口被占用

```bash
# 查看占用进程
lsof -i :8080

# 停止进程
kill -9 <PID>
```

### 问题2: Dashboard页面空白

1. 检查浏览器控制台（F12）是否有JavaScript错误
2. 确认 `dashboard.html` 文件存在
3. 检查API是否正常：`curl http://localhost:8080/api/dashboard/stats`

### 问题3: 报告无法显示

1. 确认 `output/html/` 目录下有报告文件
2. 检查文件权限：`ls -la output/html/`
3. 运行一次TrendRadar生成报告：`python3 run_with_tenders.py`

### 问题4: 招标信息为空

1. 确认 `output/tenders/` 目录下有JSON文件
2. 检查JSON文件格式是否正确
3. 运行Windows客户端或本地采集器

---

## 🔄 更新和维护

### 更新Dashboard

```bash
cd /mnt/oldroot/home/bird/TrendRadar
git pull origin feature/tender-monitoring

# 重启服务
./start_dashboard.sh
```

### 清理旧数据

```bash
# 删除30天前的报告（可选）
find output/html -name "*.html" -mtime +30 -delete

# 删除旧的招标JSON（保留最近50个）
cd output/tenders
ls -t *.json | tail -n +51 | xargs rm -f
```

---

## 📞 技术支持

- GitHub Issues: https://github.com/youyouhe/TrendRadar/issues
- 文档仓库: `DASHBOARD_GUIDE.md`（本文档）

---

## 🎉 总结

TrendRadar Dashboard 提供了一个**现代化的Web界面**，解决了之前只有静态HTML文件的问题：

✅ **统一入口** - 一个地址访问所有数据
✅ **实时查看** - 最新报告和招标信息
✅ **历史浏览** - 查看所有历史记录
✅ **搜索功能** - 快速查找招标项目
✅ **API接口** - 支持程序化访问
✅ **推送集成** - Windows客户端无缝对接

现在您可以通过 **http://localhost:8080** 访问所有TrendRadar数据！🚀
