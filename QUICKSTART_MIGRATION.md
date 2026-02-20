# TrendRadar 快速启动指南

## 🎉 迁移完成!

tender-monitor-demo 已成功迁移到 TrendRadar，现在使用 agent-browser + DeepSeek 智能采集方案。

---

## ⚡ 快速启动

### 1. 确认环境

```bash
# 确保在项目目录
cd /mnt/oldroot/home/bird/TrendRadar

# 确认.env配置
cat .env
# 应包含: DEEPSEEK_API_KEY=sk-xxxxx
```

### 2. 运行测试

```bash
python3 test_startup.py
```

预期输出:
```
✅ 数据库测试通过
✅ 解析器测试通过
✅ API路由测试通过
✅ 所有测试通过!
```

### 3. 启动服务

```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

### 4. 访问系统

- **Web界面**: http://localhost:8080/
- **API文档**: http://localhost:8080/docs (Swagger UI)
- **健康检查**: http://localhost:8080/api/health

---

## 📝 使用示例

### 示例1: 查询采集源

```bash
curl http://localhost:8080/api/sources
```

### 示例2: 创建采集任务

```bash
curl -X POST http://localhost:8080/api/collect \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": 1,
    "keywords": ["软件开发"],
    "max_items": 5
  }'
```

返回:
```json
{
  "success": true,
  "task_id": "task_1708408800_abc123",
  "message": "采集任务已创建"
}
```

### 示例3: 查询任务状态

```bash
curl http://localhost:8080/api/collect/tasks/task_1708408800_abc123
```

### 示例4: 查询招标列表

```bash
curl "http://localhost:8080/api/tenders?keyword=软件&page=1&limit=10"
```

### 示例5: 导出CSV

```bash
curl "http://localhost:8080/api/tenders/export?keyword=软件" > tenders.csv
```

---

## 🔄 与 Go 版本对比

| 功能 | Go版本 (tender-monitor-demo) | Python版本 (TrendRadar) |
|------|----------------------------|------------------------|
| **采集方式** | go-rod + 手动CSS选择器 | agent-browser + DeepSeek智能解析 |
| **页面改版适应性** | ❌ 需要重写选择器 | ✅ 自动适应 |
| **采集成本** | 免费（本地解析） | ¥0.02~0.03/次（极低） |
| **API框架** | net/http (标准库) | FastAPI (现代化) |
| **API文档** | 无 | ✅ 自动生成Swagger |
| **数据库** | SQLite + 原生SQL | SQLite + SQLAlchemy ORM |
| **异步支持** | goroutine | asyncio/await |
| **启动方式** | `./tender-monitor` | `uvicorn app:app` |

---

## 🎯 核心优势

### 1. 智能解析更鲁棒
```python
# Go版本 - 硬编码选择器
selector := "#mainContent > div.list > table > tbody > tr"

# Python版本 - LLM智能解析
projects = await parser.parse_search_results(html)
# 页面结构改变后仍能正常工作!
```

### 2. 成本极低
- 列表解析: ¥0.02/次
- 详情解析: ¥0.03/次
- **采集10个项目总成本: <¥0.35**

### 3. 开发效率高
```python
# 定义模型
class Tender(Base):
    __tablename__ = "tenders"
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    # ...

# 查询数据
tenders = await session.execute(
    select(Tender).where(Tender.status == "active")
)
```

### 4. 自动API文档
访问 http://localhost:8080/docs 即可看到完整的API文档和测试界面。

---

## 📂 项目结构

```
TrendRadar/
├── app.py                      # FastAPI主应用 ✨
├── requirements.txt            # Python依赖 ✨
├── .env                        # 配置文件
│
├── api/                        # REST API ✨
│   ├── tenders.py              # 招标查询API
│   ├── collect.py              # 采集任务API
│   ├── sources.py              # 采集源管理API
│   └── tags.py                 # 标签管理API
│
├── crawler/                    # 采集引擎 ✨
│   ├── collector.py            # 采集协调器
│   ├── task_manager.py         # 任务管理器
│   └── parsers/
│       └── deepseek_parser.py  # DeepSeek解析器
│
├── database/                   # 数据库层 ✨
│   ├── models.py               # SQLAlchemy模型
│   └── db.py                   # 数据库连接
│
├── static/                     # 前端 ✨
│   └── index.html              # Web UI
│
├── data/                       # 数据目录
│   └── tenders.db              # SQLite数据库
│
└── trendradar/                 # 原有模块
    └── crawler/
        └── agent_browser.py    # AgentBrowser封装

✨ 标记的文件为迁移过程中新创建的
```

---

## 🚀 下一步

### 立即可做
1. 启动服务: `uvicorn app:app --host 0.0.0.0 --port 8080 --reload`
2. 测试采集: 在Web界面或API创建采集任务
3. 查看结果: 在数据库或Web界面查看采集的招标信息

### 后续增强
1. **定时任务**: 使用APScheduler定时自动采集
2. **通知功能**: 匹配到关键项目时邮件/微信通知
3. **数据分析**: 招标趋势分析、预算统计
4. **Docker部署**: 一键部署到生产环境

---

## ❓ 常见问题

### Q: 如何添加新的采集源?

**方法1: 通过API**
```bash
curl -X POST http://localhost:8080/api/sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "新省份政府采购网",
    "code": "newprovince",
    "category": "province",
    "base_url": "https://example.gov.cn",
    "description": "新省份采购网站"
  }'
```

**方法2: 在数据库中手动添加**
```sql
INSERT INTO sources (name, code, category, base_url)
VALUES ('新省份政府采购网', 'newprovince', 'province', 'https://example.gov.cn');
```

### Q: 采集任务卡住怎么办?

1. 查看任务状态: `GET /api/collect/tasks/{task_id}`
2. 取消任务: `POST /api/collect/tasks/{task_id}/cancel`
3. 检查日志: 查看uvicorn输出的错误信息

### Q: 如何调整采集数量?

在创建任务时设置 `max_items`:
```json
{
  "source_id": 1,
  "keywords": ["软件开发"],
  "max_items": 20  // 最多采集20个
}
```

---

## 📊 性能建议

### 并发采集
目前任务是串行执行的。如需并行采集多个省份，可以:
```python
# 同时创建多个任务
tasks = []
for source_id in [1, 2, 3]:
    task = await task_manager.create_task(...)
    tasks.append(task)
```

### 数据库优化
如果数据量超过10万条，建议:
1. 升级到PostgreSQL
2. 添加全文索引
3. 使用Redis缓存查询结果

---

## 📞 支持

- **文档**: `MIGRATION_COMPLETE.md` - 详细的迁移报告
- **API文档**: http://localhost:8080/docs - 在线API测试
- **测试脚本**: `test_startup.py` - 系统自检

---

**祝使用愉快! 🎉**
