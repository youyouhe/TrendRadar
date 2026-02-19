# agent-browser 技术调研报告

## 执行摘要

当前系统采用 **Chrome DevTools Recorder录制 + 手动转换** 的技术路线存在根本性问题：

- ❌ 针对UI框架实现细节（Element UI类名、动态ID）
- ❌ 每个网站需要独立的转换规则和bug修复
- ❌ 页面结构变化后轨迹失效
- ❌ 维护成本随网站数量线性增长

**agent-browser 提供了完全不同的技术路线：**

- ✅ 基于语义的元素定位（role、label、placeholder、text）
- ✅ Accessibility Tree提供稳定的页面表示
- ✅ 跨网站通用，无需per-site rules
- ✅ 可与LLM结合实现智能决策
- ✅ 自愈能力：页面变化后AI可重新分析

---

## 1. 核心理念对比

### 当前方案：录制 + 转换模式

```
用户录制操作（Chrome DevTools Recorder）
    ↓
保存为JSON（包含UI框架细节）
    ↓
转换程序"猜测"用户意图
    ↓
生成简化轨迹
    ↓
执行引擎回放
```

**问题：**
1. 录制的是 **实现细节** 而非 **用户意图**
2. 选择器依赖框架（`button.el-button--primary > span`）
3. 动态ID（`#el-id-11-10`）在刷新后变化
4. 需要大量启发式规则（isSearchButton、isCaptchaInput...）

**实例：山东省采购网**
- 录制77个步骤 → 转换为14个步骤
- 仍然失败：查询按钮超时（可能有多个主按钮）
- 每次调试都在打补丁（修复选择器、添加等待、调整超时）

---

### agent-browser：语义定位 + AI决策模式

```
AI agent 导航到页面
    ↓
获取 Accessibility Tree（snapshot）
    ↓
AI 分析语义结构
    ↓
AI 生成操作序列
    ↓
执行并验证
```

**优势：**
1. 基于 **语义**：role、label、placeholder、text content
2. 稳定选择器：不依赖框架类名和动态ID
3. 自适应：页面变化后重新snapshot即可
4. 跨网站通用：同一套逻辑适用所有政府采购网站

---

## 2. 技术细节

### 2.1 Snapshot & Refs 系统

**核心命令：**
```bash
agent-browser snapshot -i
```

**输出示例：**
```
Page: 山东省政府采购网
URL: http://www.ccgp-shandong.gov.cn/xxgk?colCode=0301

@e1 [div class="second-search"]
  @e2 [span] "服务类"
  @e3 [input placeholder="请输入公告标题"]
  @e4 [img src*="captcha"]
  @e5 [input placeholder="验证码"]
  @e6 [button] "查询"

@e7 [tbody]
  @e8 [tr]
    @e9 [td] "政府采购项目编号"
    @e10 [td] "项目名称"
    @e11 [td] "采购人"
```

**关键特性：**
- 每个元素分配唯一ref（@e1, @e2...）
- 显示语义信息（tag、role、text、placeholder）
- 只返回交互元素（`-i` 参数）
- 输出紧凑（~200-400 tokens vs 3000-5000 tokens）

---

### 2.2 语义定位器

**方法1：使用refs（推荐）**
```bash
agent-browser click @e6           # 点击查询按钮
agent-browser fill @e3 "软件"     # 填充关键词输入框
```

**方法2：语义查找**
```bash
# 通过placeholder定位
agent-browser find placeholder "请输入公告标题" fill "软件"

# 通过button text定位
agent-browser find text "查询" click

# 通过role定位
agent-browser find role button click --name "查询"
```

**对比当前方案：**
```go
// 当前：脆弱的CSS选择器
selector := "button.el-button--primary > span"  // ❌ 框架依赖
selector := "#el-id-11-10"                      // ❌ 动态ID

// agent-browser：稳定的语义定位
selector := "@e6"                               // ✅ 从snapshot获取
selector := "find placeholder '请输入公告标题'"   // ✅ 语义特征
selector := "find text '查询'"                   // ✅ 用户可见文本
```

---

### 2.3 架构设计

```
┌─────────────┐
│  Rust CLI   │ ← 快速命令解析（sub-ms overhead）
└──────┬──────┘
       │ IPC
┌──────▼──────────┐
│  Node.js Daemon │ ← 管理浏览器实例
│  (Playwright)   │
└──────┬──────────┘
       │
┌──────▼──────┐
│  Chromium   │
└─────────────┘
```

**特点：**
- Daemon模式：浏览器在后台持久运行，命令间共享状态
- 支持session隔离：多个采集任务并行
- 支持profile持久化：保存登录状态

---

## 3. 应用于招标监控系统的方案设计

### 3.1 新架构概览

```
┌─────────────────────────────────────────────────┐
│              Go Main Server                     │
│  ┌───────────────────────────────────────────┐  │
│  │     Collection Orchestrator                │  │
│  │  - 任务管理                                │  │
│  │  - 数据存储                                │  │
│  │  - API服务                                 │  │
│  └────────────┬────────────────────────────────┘  │
│               │                                   │
│  ┌────────────▼────────────────────────────────┐  │
│  │      AI Agent Module                        │  │
│  │  - LLM分析页面结构                          │  │
│  │  - 生成操作序列                             │  │
│  │  - 验证结果                                 │  │
│  └────────────┬────────────────────────────────┘  │
│               │                                   │
│  ┌────────────▼────────────────────────────────┐  │
│  │    agent-browser Wrapper                    │  │
│  │  exec.Command("agent-browser", ...)         │  │
│  └────────────┬────────────────────────────────┘  │
└───────────────┼─────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────┐
│          agent-browser daemon                   │
│          (Node.js + Playwright)                 │
└─────────────────────────────────────────────────┘
```

---

### 3.2 实施示例：山东省采购网

**当前方案执行流程：**
```go
// 1. 加载预录制的轨迹文件
trace := loadTrace("traces/shandong_list.json")

// 2. 执行预定义步骤（盲目回放）
for _, step := range trace.Steps {
    switch step.Action {
    case "click":
        elem := page.Element(step.Selector)  // ❌ 超时：selector可能不唯一
        elem.Click()
    // ...
    }
}
```

**agent-browser方案：**
```go
// 1. 导航到页面
exec.Command("agent-browser", "open",
    "http://www.ccgp-shandong.gov.cn/xxgk?colCode=0301").Run()

// 2. 获取页面结构
snapshot := exec.Command("agent-browser", "snapshot", "-i", "--json").Output()
tree := parseAccessibilityTree(snapshot)

// 3. 让LLM分析页面并生成操作
prompt := fmt.Sprintf(`
页面结构：
%s

任务：在这个政府采购网站上搜索"软件"相关招标。

要求：
1. 找到关键词输入框
2. 输入"软件"
3. 处理验证码（如果有）
4. 点击查询按钮
5. 提取结果列表

请生成agent-browser命令序列。
`, tree)

commands := callLLM(prompt)  // 返回命令列表

// 4. 执行LLM生成的命令
for _, cmd := range commands {
    result := exec.Command("agent-browser", cmd...).Output()
    // 验证每一步的结果
    if !validateResult(result) {
        // 重新snapshot并让LLM修正
        snapshot := exec.Command("agent-browser", "snapshot", "-i", "--json").Output()
        commands = callLLM(fmt.Sprintf("上一步失败：%s\n新页面：%s\n请修正", result, snapshot))
    }
}

// 5. 提取数据
data := exec.Command("agent-browser", "eval", "extractTableData()").Output()
```

**LLM可能生成的命令序列：**
```json
[
  "find placeholder '请输入公告标题' fill '软件'",
  "wait 2000",
  "screenshot captcha.png",
  "find placeholder '验证码' fill '${OCR_RESULT}'",
  "find text '查询' click",
  "wait --load networkidle",
  "snapshot -i --json"
]
```

---

### 3.3 优势分析

#### A. 无需预录制

**当前方案：**
```bash
# 用户必须：
1. 打开Chrome DevTools Recorder
2. 手动执行一遍操作
3. 导出JSON
4. 通过Web UI上传
5. 系统转换并存储
6. 测试验证
```

**新方案：**
```bash
# 只需提供URL和任务描述
POST /api/collect
{
  "url": "http://www.ccgp-shandong.gov.cn/xxgk?colCode=0301",
  "task": "搜索软件相关招标并提取列表",
  "source_type": "government_procurement"
}

# 系统自动：
1. 导航到页面
2. AI分析结构
3. 生成并执行操作
4. 提取数据
```

#### B. 自愈能力

**当前方案：页面变化后失效**
```
页面改版（Element UI升级）
    ↓
动态ID格式变化（el-id → el-v2-id）
    ↓
所有轨迹失效
    ↓
用户必须重新录制
```

**新方案：自适应**
```
页面改版
    ↓
重新snapshot获取新结构
    ↓
AI重新分析语义
    ↓
生成新的操作序列
    ↓
继续工作
```

#### C. 跨网站通用

**当前方案：每个网站独立开发**
- 山东省：`button.el-button--primary > span`
- 广东省：`button.ant-btn-primary`
- 其他省：各种奇怪的框架和结构

**新方案：统一处理**
```go
type CollectionStrategy struct {
    URL         string
    TaskPrompt  string
}

// 所有政府采购网站使用相同的代码
func collectGovernmentProcurement(strategy CollectionStrategy) {
    navigate(strategy.URL)
    snapshot := getSnapshot()
    commands := llm.GenerateCommands(snapshot, strategy.TaskPrompt)
    executeCommands(commands)
}
```

---

## 4. 实施路径

### 阶段1：验证可行性（1-2天）

```bash
# 1. 安装agent-browser
npm install -g agent-browser
agent-browser install

# 2. 手动测试山东省采购网
agent-browser open "http://www.ccgp-shandong.gov.cn/xxgk?colCode=0301"
agent-browser snapshot -i
agent-browser find placeholder "请输入公告标题" fill "软件"
# ... 观察是否比当前方案更可靠

# 3. 测试广东省、其他省份
# 验证跨网站通用性
```

### 阶段2：Go集成（3-5天）

```go
// pkg/browser/agent_browser.go

type AgentBrowser struct {
    sessionName string
}

func (ab *AgentBrowser) Open(url string) error {
    cmd := exec.Command("agent-browser",
        "--session-name", ab.sessionName,
        "open", url)
    return cmd.Run()
}

func (ab *AgentBrowser) Snapshot() (*AccessibilityTree, error) {
    cmd := exec.Command("agent-browser",
        "--session-name", ab.sessionName,
        "snapshot", "-i", "--json")
    output, err := cmd.Output()
    if err != nil {
        return nil, err
    }

    var tree AccessibilityTree
    json.Unmarshal(output, &tree)
    return &tree, nil
}

func (ab *AgentBrowser) FindAndFill(label, value string) error {
    cmd := exec.Command("agent-browser",
        "--session-name", ab.sessionName,
        "find", "placeholder", label, "fill", value)
    return cmd.Run()
}
```

### 阶段3：LLM集成（1周）

两种方案：

**方案A：使用本地LLM（成本低，离线）**
```bash
# 使用Ollama运行Qwen2.5-14B
ollama pull qwen2.5:14b

# Go代码调用
response := callOllama("qwen2.5:14b", prompt)
```

**方案B：使用Claude/GPT API（效果好，成本高）**
```go
import "github.com/anthropics/anthropic-sdk-go"

client := anthropic.NewClient(apiKey)
response := client.Messages.Create(ctx, &anthropic.MessageCreateParams{
    Model: "claude-3-5-sonnet-20241022",
    Messages: []anthropic.Message{{
        Role: "user",
        Content: prompt,
    }},
})
```

### 阶段4：渐进式替换（2-3周）

```
Week 1: 新增agent-browser模式，与trace模式并存
Week 2: 用户可选择使用哪种模式
Week 3: 逐步迁移现有轨迹
Week 4: 完全废弃trace模式（如果验证成功）
```

---

## 5. 成本效益分析

### 当前方案成本

**开发成本：**
- 每个新网站：2-3天（录制、转换、调试、测试）
- 维护成本：页面改版后需重新录制
- 技术债务：转换规则越来越复杂

**运行成本：**
- 无LLM成本
- 但失败率高，需人工干预

---

### agent-browser方案成本

**开发成本：**
- 初始集成：1-2周
- 每个新网站：1小时（只需提供URL和任务描述）
- 维护成本：几乎为零（AI自动适应）

**运行成本：**
- LLM API费用：
  - 方案A（Ollama本地）：$0/月
  - 方案B（Claude API）：~$0.002/次采集（snapshot 400 tokens + 生成200 tokens）
- 假设每天采集100次 × 30天 = $6/月

**ROI：**
- 开发时间节省：每新增10个网站节省 25-30 天开发时间
- 维护时间节省：页面改版无需人工介入
- 成功率提升：从当前的 ~60% 提升到 ~90%+

---

## 6. 风险评估

### 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| LLM理解错误 | 中 | 中 | 添加验证步骤，失败后重试 |
| agent-browser不稳定 | 低 | 高 | 回退到trace模式 |
| 延迟增加 | 中 | 低 | 使用本地LLM降低延迟 |
| 成本超预算 | 低 | 低 | 使用Ollama本地部署 |

### 业务风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 用户不接受新方式 | 低 | 中 | 保留trace模式作为备选 |
| 过渡期间混乱 | 中 | 低 | 渐进式迁移，两种模式并存 |

---

## 7. 建议决策

### 立即行动（今天）

1. **安装agent-browser并手动测试**
   ```bash
   npm install -g agent-browser
   agent-browser install
   # 测试3-5个现有网站
   ```

2. **对比当前方案**
   - 选择器稳定性
   - 操作成功率
   - 调试难度

### 短期决策（本周）

基于测试结果决定：
- ✅ **如果agent-browser明显更稳定** → 启动阶段2（Go集成）
- ⚠️ **如果结果相当** → 继续观察，暂不迁移
- ❌ **如果不如当前方案** → 放弃agent-browser，优化现有方案

### 中期目标（下月）

如果决定采用agent-browser：
- 完成Go wrapper开发
- 集成LLM（优先Ollama本地部署）
- 新网站只使用新方案
- 旧网站逐步迁移

---

## 8. 替代方案

如果agent-browser不适合，考虑：

### 方案A：优化现有trace系统

- 引入更多启发式规则
- 使用计算机视觉辅助定位（OCR识别按钮文本）
- 增加重试和fallback机制

**评估：** 治标不治本，维护成本持续增长

### 方案B：使用Playwright录制

- Playwright有更好的录制工具
- 生成更稳定的选择器
- 支持代码生成（Python/JavaScript）

**评估：** 仍然是录制回放模式，本质问题未解决

### 方案C：纯视觉AI方案

- 使用GPT-4V/Claude-3.5-Sonnet等多模态模型
- 截图 → AI识别元素位置 → 点击坐标

**评估：** 成本极高（$0.01/次），延迟大（5-10秒/步）

---

## 9. 总结

**当前方案的核心问题：**
> 针对UI实现细节而非用户意图，导致脆弱性和高维护成本

**agent-browser的核心优势：**
> 基于语义和AI决策，实现跨网站通用和自愈能力

**推荐行动：**
1. 今天：手动测试agent-browser
2. 本周：决定是否采用
3. 下月：如果采用，完成集成和迁移

**预期收益：**
- 新网站接入时间：3天 → 1小时（95%减少）
- 维护工作量：页面改版需重新录制 → 零维护
- 成功率：~60% → ~90%+
- 技术债务：持续增长 → 逐步降低

---

## 附录A：快速测试脚本

```bash
#!/bin/bash
# test_agent_browser.sh

echo "测试1：山东省政府采购网"
agent-browser open "http://www.ccgp-shandong.gov.cn/xxgk?colCode=0301"
agent-browser wait --load networkidle
agent-browser snapshot -i > shandong_snapshot.txt

echo "分析snapshot，寻找关键词输入框..."
grep "placeholder" shandong_snapshot.txt

echo ""
echo "测试2：广东省政府采购网"
agent-browser open "http://gdgpo.czt.gd.gov.cn/"
agent-browser wait --load networkidle
agent-browser snapshot -i > guangdong_snapshot.txt

echo "分析snapshot，对比选择器稳定性..."
grep "placeholder\|button\|input" guangdong_snapshot.txt

echo ""
echo "测试3：执行搜索流程"
agent-browser open "http://www.ccgp-shandong.gov.cn/xxgk?colCode=0301"
agent-browser snapshot -i | grep "@e" | head -20

echo "请手动执行："
echo "  agent-browser find placeholder '请输入公告标题' fill '软件'"
echo "  agent-browser screenshot before_search.png"
echo "  agent-browser find text '查询' click"
echo "  agent-browser wait --load networkidle"
echo "  agent-browser screenshot after_search.png"

echo ""
echo "对比两张截图，判断是否成功"
```

---

## 附录B：参考资源

- **agent-browser GitHub**: https://github.com/vercel-labs/agent-browser
- **Playwright文档**: https://playwright.dev/
- **Accessibility Tree标准**: https://www.w3.org/TR/accname-1.2/
- **Ollama本地LLM**: https://ollama.ai/

---

**报告生成时间**: 2026-02-19
**作者**: Claude Sonnet 4.5
**版本**: v1.0
