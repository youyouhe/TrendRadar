# 招标信息整合到TrendRadar - 实施方案

## 方案总结

将招标信息作为TrendRadar的一个信息源，在HTML报告中独立展示。

### 整合方式

✅ **展示方式**：在TrendRadar HTML报告的"独立展示区"显示招标信息
✅ **功能保留**：数据库历史记录 + 关键词过滤 + 自动采集 + AI分析

---

## 架构设计

```
TrendRadar (热点新闻聚合)
├── 热榜平台 (微博、知乎、百度等)
├── RSS 源 (技术博客、新闻等)
└── 招标信息源 ← 新增！
    ├── agent-browser + DeepSeek 智能采集
    ├── SQLite 数据库（历史记录）
    ├── 关键词过滤（复用 frequency_words.txt）
    └── 在HTML报告"独立展示区"显示
```

---

## 已完成的工作

### 1. 后端基础设施 ✅

**文件**: `database/`, `crawler/`, `api/`

- SQLAlchemy 数据库模型（Sources, Tenders, Tags, Tasks）
- agent-browser + DeepSeek 智能采集引擎
- FastAPI REST API（可选，用于独立管理）
- 异步任务管理器

### 2. TrendRadar整合模块 ✅

**文件**: `trendradar/crawler/tender.py`

- `TenderCollector` - 招标采集器类
- `fetch_tender_data()` - TrendRadar调用接口
- 支持多个采集源并行
- 自动使用DeepSeek解析HTML

### 3. 配置文件 ✅

**文件**: `config/tender_sources.yaml`

```yaml
TENDER_ENABLED: true

TENDER_SOURCES:
  - id: beijing
    name: 北京市政府采购网
    url: http://www.ccgp-beijing.gov.cn/
    enabled: true

TENDER_SETTINGS:
  MAX_ITEMS_PER_SOURCE: 10
  USE_KEYWORD_FILTER: true        # 使用 frequency_words.txt
  INCLUDE_IN_AI_ANALYSIS: true
```

### 4. 整合启动脚本 ✅

**文件**: `run_with_tenders.py`

在TrendRadar主流程中添加招标采集，并保存数据到 `output/tenders/`。

---

## 使用方式

### 方式A: 独立FastAPI服务（推荐用于管理）

适合需要Web界面管理招标数据库的场景。

```bash
# 1. 启动FastAPI服务
uvicorn app:app --host 0.0.0.0 --port 8080

# 2. 访问API文档
open http://localhost:8080/docs

# 3. 创建采集任务
curl -X POST http://localhost:8080/api/collect \
  -H "Content-Type: application/json" \
  -d '{"source_id": 1, "keywords": ["软件开发"], "max_items": 5}'

# 4. 查询招标列表
curl "http://localhost:8080/api/tenders?keyword=软件"
```

**优点**:
- 完整的Web API
- 数据库管理
- 任务监控
- CSV导出

### 方式B: 整合到TrendRadar（推荐用于报告）

适合需要在TrendRadar HTML报告中展示招标信息的场景。

```bash
# 1. 配置招标源
vim config/tender_sources.yaml

# 2. 运行整合版
python3 run_with_tenders.py

# 3. 查看结果
ls output/tenders/   # 招标数据JSON文件
ls output/html/      # TrendRadar HTML报告
```

**工作流程**:
1. 先采集招标信息（agent-browser + DeepSeek）
2. 保存到 `output/tenders/` 目录
3. 运行TrendRadar主程序（热榜 + RSS）
4. *(待实现)* 在HTML报告中添加"招标信息"独立展示区

---

## 待完成的工作

### 1. 修改HTML报告生成器 ⏳

**需要修改的文件**: `trendradar/report/html.py` 或相关模板

添加招标信息展示区，类似RSS独立展示区的格式：

```html
<div class="tender-section">
  <h2>🏢 招标信息</h2>
  <div class="tender-items">
    {% for tender in tenders %}
    <div class="tender-item">
      <h3>{{ tender.title }}</h3>
      <div class="tender-meta">
        <span>预算: {{ tender.budget }}万元</span>
        <span>截止: {{ tender.deadline }}</span>
        <span>联系: {{ tender.contact_person }}</span>
      </div>
      <a href="{{ tender.url }}">查看详情 →</a>
    </div>
    {% endfor %}
  </div>
</div>
```

### 2. 完全整合到 NewsAnalyzer ⏳

**需要修改的文件**: `trendradar/__main__.py`

在 `NewsAnalyzer` 类的 `run()` 方法中添加：

```python
def run(self) -> None:
    """执行分析流程"""
    try:
        # ... 现有代码 ...

        # 抓取热榜数据
        results, id_to_name, failed_ids = self._crawl_data()

        # 抓取 RSS 数据
        rss_items, rss_new_items, raw_rss_items = self._crawl_rss_data()

        # ⬇️ 新增：抓取招标数据
        tender_items = self._crawl_tender_data()

        # 执行模式策略，传递所有数据
        self._execute_mode_strategy(
            mode_strategy, results, id_to_name, failed_ids,
            rss_items=rss_items,
            rss_new_items=rss_new_items,
            raw_rss_items=raw_rss_items,
            tender_items=tender_items  # ⬅️ 新增参数
        )
```

并添加采集方法：

```python
def _crawl_tender_data(self) -> Optional[List[Dict]]:
    """执行招标数据抓取"""
    tender_config = load_tender_config()

    if not tender_config or not tender_config.get('TENDER_ENABLED', False):
        return None

    from trendradar.crawler.tender import fetch_tender_data

    # 提取关键词
    word_groups, _, _ = self.ctx.load_frequency_words()
    keywords = []
    if word_groups:
        keywords = word_groups[0].get('keywords', [])[:3]

    sources = [s for s in tender_config.get('TENDER_SOURCES', [])
               if s.get('enabled', True)]

    tenders = fetch_tender_data(
        sources=sources,
        keywords=keywords,
        max_items_per_source=10
    )

    print(f"[招标] 采集完成：{len(tenders)} 条")
    return tenders
```

### 3. AI分析招标趋势 ⏳

在 `trendradar/ai/analyzer.py` 中添加招标数据分析：

- 预算趋势分析
- 热门关键词统计
- 采购单位排名
- 时间分布分析

### 4. 通知推送招标信息 ⏳

在 `trendradar/notification/` 中添加招标通知：

- 飞书/钉钉/企业微信通知
- 邮件通知（包含招标详情）
- Telegram/Bark推送

---

## 配置说明

### 1. 环境变量

```bash
# .env 文件
DEEPSEEK_API_KEY=sk-xxxxx    # 必需：DeepSeek API密钥
DATA_DIR=./data               # 可选：数据目录
```

### 2. 招标源配置

```yaml
# config/tender_sources.yaml

TENDER_ENABLED: true   # 启用/禁用招标采集

TENDER_SOURCES:
  - id: beijing        # 唯一标识
    name: 北京市政府采购网
    url: http://www.ccgp-beijing.gov.cn/
    enabled: true      # 是否启用此源

TENDER_SETTINGS:
  MAX_ITEMS_PER_SOURCE: 10           # 每个源最多采集数量
  USE_KEYWORD_FILTER: true           # 使用 frequency_words.txt 过滤
  INCLUDE_IN_AI_ANALYSIS: true       # 包含在AI分析中
  REQUEST_INTERVAL: 2000             # 请求间隔（毫秒）
```

### 3. 关键词过滤

招标信息会使用 `config/frequency_words.txt` 中的关键词过滤。

示例：
```txt
# config/frequency_words.txt
[软件开发]
软件
系统
信息化
智慧
云平台
```

---

## 数据流程

```
1. 触发采集
   ├─ 手动: python3 run_with_tenders.py
   ├─ API: POST /api/collect
   └─ 定时: crontab / GitHub Actions

2. agent-browser 访问采集源
   ├─ 导航到政府采购网站
   ├─ 输入关键词搜索
   └─ 获取HTML内容

3. DeepSeek 智能解析
   ├─ 列表页：提取项目标题、URL
   └─ 详情页：提取预算、联系人、截止日期

4. 数据处理
   ├─ 去重（基于URL）
   ├─ 关键词过滤
   └─ 保存到SQLite

5. 展示
   ├─ FastAPI: /api/tenders查询
   ├─ TrendRadar: HTML报告独立展示区
   └─ 通知: 飞书/钉钉/邮件推送
```

---

## 成本估算

**DeepSeek API成本**:
- 列表页解析: ¥0.02/次
- 详情页解析: ¥0.03/次
- 采集10个项目: ¥0.02 + ¥0.30 = **¥0.32**

**每日成本**（按3个源，每源10个项目）:
- 3个源 × 10个项目 × ¥0.32 = **¥9.6/天**
- 约 **¥290/月**

---

## 故障排查

### 问题1: "未找到DEEPSEEK_API_KEY"

```bash
# 确保.env文件存在并包含API密钥
echo "DEEPSEEK_API_KEY=sk-xxxxx" > .env
```

### 问题2: 浏览器启动失败

```bash
# 安装Chromium
apt-get install chromium-browser   # Ubuntu
brew install chromium              # macOS
```

### 问题3: 前端显示"需要轨迹文件"

删除独立前端UI，使用TrendRadar整合版：
```bash
rm static/index.html
python3 run_with_tenders.py
```

---

## 后续扩展

### 1. 多省份并行采集
添加更多采集源到 `config/tender_sources.yaml`。

### 2. 定时自动采集
```bash
# crontab -e
0 9 * * * cd /path/to/TrendRadar && python3 run_with_tenders.py
```

### 3. 招标预测
基于历史数据预测招标趋势。

### 4. 导出报告
生成PDF/Word格式的招标分析报告。

---

## 总结

✅ **已完成**: 数据库 + 采集引擎 + API + 配置
⏳ **待完成**: HTML展示 + AI分析 + 通知推送

**当前可用**:
- 独立FastAPI服务管理招标数据
- 采集并保存到JSON文件
- REST API查询和导出

**最终目标**:
- 在TrendRadar HTML报告中显示招标信息
- 与热榜、RSS数据一起分析推送
- 统一的调度和通知机制

---

**更新日期**: 2026-02-20
**项目路径**: `/mnt/oldroot/home/bird/TrendRadar`
