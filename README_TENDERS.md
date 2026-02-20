# TrendRadar + 招标信息整合版

## 概述

将招标信息采集整合到TrendRadar框架中，作为独立信息源展示。

### 为什么整合到TrendRadar？

- ✅ **统一平台**: 热榜 + RSS + 招标信息，一站式查看
- ✅ **智能解析**: agent-browser + DeepSeek，页面改版后仍能工作
- ✅ **关键词过滤**: 复用 `frequency_words.txt`，只看关心的项目
- ✅ **AI分析**: 可选的DeepSeek趋势分析
- ✅ **统一推送**: 一起推送到飞书/钉钉/邮件

---

## 快速开始

### 1. 配置

```bash
# 1.1 设置DeepSeek API密钥
echo "DEEPSEEK_API_KEY=sk-xxxxx" >> .env

# 1.2 配置招标采集源
vim config/tender_sources.yaml
```

`config/tender_sources.yaml` 示例：
```yaml
TENDER_ENABLED: true

TENDER_SOURCES:
  - id: beijing
    name: 北京市政府采购网
    url: http://www.ccgp-beijing.gov.cn/
    enabled: true   # 改为true启用
```

### 2. 运行

#### 方式A: 独立FastAPI服务

适合需要管理招标数据库、查询历史记录的场景。

```bash
# 启动服务
uvicorn app:app --host 0.0.0.0 --port 8080

# API文档
open http://localhost:8080/docs

# 创建采集任务
curl -X POST http://localhost:8080/api/collect \
  -H "Content-Type: application/json" \
  -d '{"source_id": 1, "keywords": ["软件开发"], "max_items": 5}'
```

#### 方式B: 整合到TrendRadar

适合需要在HTML报告中查看招标信息的场景。

```bash
# 运行整合版（先采集招标，再运行TrendRadar）
python3 run_with_tenders.py

# 查看结果
ls output/tenders/  # 招标数据JSON
ls output/html/     # TrendRadar HTML报告
```

---

## 两种模式对比

| 特性 | 独立FastAPI服务 | TrendRadar整合版 |
|------|---------------|----------------|
| **适用场景** | 管理招标数据库 | 查看综合报告 |
| **Web UI** | Swagger API文档 | TrendRadar HTML |
| **数据存储** | SQLite数据库 | JSON文件 + SQLite |
| **历史查询** | ✅ 支持 | ⏳ 待实现 |
| **HTML报告** | ❌ 无 | ✅ 在独立展示区 |
| **与热榜/RSS整合** | ❌ 独立 | ✅ 统一展示 |
| **AI分析** | ❌ 无 | ⏳ 待实现 |
| **通知推送** | ❌ 无 | ⏳ 待实现 |

---

## 当前状态

### ✅ 已完成

1. **后端完整**：数据库 + 采集引擎 + API
2. **智能采集**：agent-browser + DeepSeek自动解析
3. **两种使用方式**：独立服务 + TrendRadar整合
4. **配置化**：`tender_sources.yaml` 灵活配置

### ⏳ 待完成

1. **HTML展示**：在TrendRadar HTML报告中添加"招标信息"版块
2. **完全整合**：修改 `NewsAnalyzer` 主流程
3. **AI分析**：招标趋势分析、预算统计
4. **通知推送**：飞书/钉钉/邮件通知新招标

---

## 工作流程

```
┌─────────────────────────────────────────────┐
│  1. python3 run_with_tenders.py 启动        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  2. 读取 config/tender_sources.yaml         │
│     - 启用的采集源                           │
│     - 采集数量、关键词设置                    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  3. 使用 agent-browser 访问政府采购网站      │
│     - 北京市政府采购网                       │
│     - 输入关键词搜索                         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  4. DeepSeek 智能解析 HTML                   │
│     - 列表页：提取项目标题、URL              │
│     - 详情页：提取预算、联系人、截止日期      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  5. 数据处理                                 │
│     - URL去重                                │
│     - 使用 frequency_words.txt 关键词过滤    │
│     - 保存到 output/tenders/XXX.json        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  6. 运行 TrendRadar 主程序                   │
│     - 采集热榜数据                           │
│     - 采集 RSS 数据                          │
│     - 生成 HTML 报告                         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  7. (待实现) 在HTML中显示招标信息            │
│     - 独立展示区                             │
│     - 预算、截止日期、联系人                  │
└─────────────────────────────────────────────┘
```

---

## 示例输出

### 采集结果（JSON）

```json
{
  "title": "北京市石景山区教育信息化建设项目",
  "budget": "150",
  "publish_date": "2026-02-15",
  "deadline": "2026-03-01 14:00",
  "contact_person": "张老师",
  "contact_phone": "010-12345678",
  "purchaser": "北京市石景山区教育委员会",
  "url": "http://www.ccgp-beijing.gov.cn/xxxx",
  "source": "北京市政府采购网",
  "collected_at": "2026-02-20T10:30:00"
}
```

### HTML报告（待实现）

```html
<div class="tender-section">
  <h2>🏢 招标信息</h2>

  <div class="tender-item">
    <h3>北京市石景山区教育信息化建设项目</h3>
    <div class="meta">
      <span class="budget">💰 预算：150万元</span>
      <span class="deadline">⏰ 截止：2026-03-01 14:00</span>
      <span class="contact">👤 联系：张老师 010-12345678</span>
    </div>
    <div class="purchaser">采购人：北京市石景山区教育委员会</div>
    <a href="http://xxx" class="detail-link">查看详情 →</a>
  </div>

  <!-- 更多招标项目... -->
</div>
```

---

## 成本

**DeepSeek API成本**（按每日3个源，每源10个项目）:
- 列表页: 3 × ¥0.02 = ¥0.06
- 详情页: 30 × ¥0.03 = ¥0.90
- **每日**: ¥0.96
- **每月**: ¥29

非常低的成本！

---

## 配置示例

### .env
```bash
DEEPSEEK_API_KEY=sk-xxxxx
DATA_DIR=./data
```

### config/tender_sources.yaml
```yaml
TENDER_ENABLED: true

TENDER_SOURCES:
  - id: beijing
    name: 北京市政府采购网
    url: http://www.ccgp-beijing.gov.cn/
    enabled: true

  - id: guangdong
    name: 广东省政府采购网
    url: https://gdgpo.czt.gd.gov.cn
    enabled: false  # 暂不启用

TENDER_SETTINGS:
  MAX_ITEMS_PER_SOURCE: 10
  USE_KEYWORD_FILTER: true  # 使用 frequency_words.txt
  INCLUDE_IN_AI_ANALYSIS: true
```

### config/frequency_words.txt
```txt
# 招标关键词（TrendRadar会自动使用）
[软件开发]
软件
系统
信息化
智慧

[硬件采购]
服务器
存储
网络设备
```

---

## 下一步工作

### 1. 修改HTML报告生成器

**文件**: `trendradar/report/html.py`

添加招标信息展示模板。

### 2. 完全整合到主流程

**文件**: `trendradar/__main__.py`

在 `NewsAnalyzer.run()` 中添加招标采集调用。

### 3. AI分析

使用DeepSeek分析：
- 招标趋势（哪些领域热门）
- 预算分布
- 时间分析（哪些时间段发布多）

### 4. 通知推送

整合到TrendRadar的通知系统：
- 飞书/钉钉/企业微信
- 邮件
- Telegram/Bark

---

## 故障排查

### Q: "未找到DEEPSEEK_API_KEY"

```bash
# 确保.env文件存在
cat .env

# 应该包含:
DEEPSEEK_API_KEY=sk-xxxxx
```

### Q: 浏览器启动失败

```bash
# 安装Chromium
# Ubuntu
sudo apt-get install chromium-browser

# macOS
brew install chromium
```

### Q: 没有采集到数据

检查配置文件:
```bash
# 确保至少有一个源是enabled: true
cat config/tender_sources.yaml | grep enabled
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `TENDER_INTEGRATION.md` | 详细的整合方案文档 |
| `run_with_tenders.py` | 整合启动脚本 |
| `config/tender_sources.yaml` | 招标源配置 |
| `trendradar/crawler/tender.py` | 招标采集模块 |
| `app.py` | FastAPI独立服务入口 |
| `database/models.py` | 数据库模型 |
| `api/tenders.py` | 招标信息API |

---

## 总结

**当前可用**:
- ✅ 独立FastAPI服务管理招标数据
- ✅ 采集并保存到JSON文件
- ✅ REST API查询和导出

**最终目标**:
- ⏳ 在TrendRadar HTML报告中显示
- ⏳ 与热榜、RSS统一分析推送
- ⏳ AI分析招标趋势

**使用建议**:
1. 立即可用：独立FastAPI服务（`uvicorn app:app`）
2. 部分可用：整合版采集数据（`python3 run_with_tenders.py`）
3. 待完善：HTML展示和完全整合

---

**更新时间**: 2026-02-20
**项目路径**: `/mnt/oldroot/home/bird/TrendRadar`
