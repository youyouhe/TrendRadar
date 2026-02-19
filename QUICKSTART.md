# TrendRadar 招标监控 - 快速开始指南

## 环境准备

### 1. 检查 Python 版本

```bash
python3 --version  # 需要 Python 3.8+
```

### 2. 安装依赖

```bash
cd /mnt/oldroot/home/bird/TrendRadar

# 安装 TrendRadar 核心依赖
pip install -r requirements.txt

# 安装额外依赖（招标监控需要）
pip install requests pillow
```

### 3. 验证 agent-browser 安装

```bash
agent-browser --version
# 应该显示: agent-browser 0.x.x
```

如果未安装：
```bash
npm install -g agent-browser
```

---

## 方案 A：简单测试（不需要真实网站）

测试 AgentBrowser 基础功能和模块导入：

```bash
cd /mnt/oldroot/home/bird/TrendRadar

# 测试模块导入
python3 -c "
from trendradar.crawler import AgentBrowser, get_tender_source
print('✓ AgentBrowser 导入成功')

source = get_tender_source('shandong')
print(f'✓ 数据源: {source.source_name}')
print(f'✓ 网站: {source.base_url}')
"
```

预期输出：
```
✓ AgentBrowser 导入成功
✓ 数据源: 山东省政府采购网
✓ 网站: http://ggzy.shandong.gov.cn/
```

---

## 方案 B：完整测试（需要验证码服务 + 真实网站）

### 步骤 1：启动验证码服务

打开**第一个终端**：

```bash
cd /mnt/oldroot/home/bird/tender-monitor-demo/captcha-service

# 激活虚拟环境（如果已创建）
source venv/bin/activate

# 如果没有虚拟环境，创建一个
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 启动验证码服务
uvicorn app:app --host 0.0.0.0 --port 5000
```

验证服务启动：
```bash
curl http://localhost:5000/health
# 应该返回: {"status":"ok","engine":"ddddocr"}
```

### 步骤 2：运行招标采集测试

打开**第二个终端**：

```bash
cd /mnt/oldroot/home/bird/TrendRadar

# 运行山东省招标采集测试
python3 test_tender_shandong.py
```

### 预期输出

```
============================================================
山东省招标信息采集测试
============================================================

✓ 数据源: 山东省政府采购网
  代码: shandong
  网站: http://ggzy.shandong.gov.cn/

搜索参数:
  关键词: ['软件开发', '系统集成']
  类别: 服务
  最大结果: 10

开始搜索...
------------------------------------------------------------
[山东省政府采购网] 访问 http://ggzy.shandong.gov.cn/
[山东省政府采购网] 选择类别: 服务类
[山东省政府采购网] 输入关键词: 软件开发
[山东省政府采购网] 验证码识别: 1234
[山东省政府采购网] 点击查询按钮
[山东省政府采购网] 提取列表数据
[山东省政府采购网] 找到 5 条结果

✓ 搜索完成，找到 5 条结果

1. XX单位软件开发项目采购公告
   发布日期: 2024-01-15
   URL: http://ggzy.shandong.gov.cn/?ref=@e10
   关键词: 软件开发

2. XX系统集成服务采购公告
   发布日期: 2024-01-16
   URL: http://ggzy.shandong.gov.cn/?ref=@e11
   关键词: 软件开发

...

============================================================
测试完成
============================================================
```

---

## 方案 C：单元测试（推荐用于开发）

创建一个简化的测试脚本：

```bash
cd /mnt/oldroot/home/bird/TrendRadar

# 创建测试脚本
cat > test_basic.py << 'EOF'
#!/usr/bin/env python3
# coding=utf-8
"""基础功能测试"""

def test_imports():
    """测试模块导入"""
    print("测试1: 模块导入...")
    try:
        from trendradar.crawler import AgentBrowser
        from trendradar.crawler.tender import TenderData, TenderSource
        from trendradar.crawler.tender import get_tender_source
        print("  ✓ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False

def test_data_structure():
    """测试数据结构"""
    print("\n测试2: TenderData 数据结构...")
    try:
        from trendradar.crawler.tender import TenderData, TenderStatus
        from datetime import datetime

        tender = TenderData(
            title="测试招标项目",
            url="http://example.com/test",
            source="shandong",
            source_name="山东省政府采购网",
            publish_date=datetime.now(),
            deadline=None,
            project_no="TEST-2024-001",
            amount="100万元",
            category="服务",
            status=TenderStatus.ACTIVE,
            keywords=["软件", "开发"],
        )

        print(f"  ✓ 创建 TenderData: {tender.title}")
        print(f"  ✓ 状态: {tender.status.value}")
        print(f"  ✓ 关键词: {tender.keywords}")

        # 测试关键词匹配
        assert tender.matches_keywords(["软件"], match_mode="any") == True
        assert tender.matches_keywords(["软件", "开发"], match_mode="all") == True
        assert tender.matches_keywords(["测试招标项目"], match_mode="exact") == True
        print("  ✓ 关键词匹配功能正常")

        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_source_registry():
    """测试数据源注册"""
    print("\n测试3: 数据源注册...")
    try:
        from trendradar.crawler.tender import get_tender_source, PROVINCE_SOURCES

        print(f"  ✓ 已注册省份: {list(PROVINCE_SOURCES.keys())}")

        source = get_tender_source("shandong")
        print(f"  ✓ 山东数据源: {source.source_name}")
        print(f"  ✓ 网站: {source.base_url}")

        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False

def test_agent_browser():
    """测试 AgentBrowser 基础功能"""
    print("\n测试4: AgentBrowser 初始化...")
    try:
        from trendradar.crawler import AgentBrowser

        # 只测试初始化，不实际启动浏览器
        browser = AgentBrowser(
            session_name="test_session",
            headless=True
        )

        print(f"  ✓ AgentBrowser 实例: {browser}")
        print(f"  ✓ 会话名称: {browser.session_name}")
        print(f"  ✓ 无头模式: {browser.headless}")

        return True
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TrendRadar 招标监控 - 基础功能测试")
    print("=" * 60)

    results = []
    results.append(test_imports())
    results.append(test_data_structure())
    results.append(test_source_registry())
    results.append(test_agent_browser())

    print("\n" + "=" * 60)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("=" * 60)

    exit(0 if all(results) else 1)
EOF

# 运行测试
python3 test_basic.py
```

---

## 常见问题

### Q1: ImportError: No module named 'requests'

**解决方案**：
```bash
pip install requests
```

### Q2: agent-browser: command not found

**解决方案**：
```bash
npm install -g agent-browser
```

### Q3: 验证码识别失败

**原因**：captcha-service 未启动或不可访问

**解决方案**：
```bash
# 检查服务状态
curl http://localhost:5000/health

# 如果未启动，参考"方案 B - 步骤 1"启动服务
```

### Q4: 山东网站访问超时

**原因**：网站可能有反爬虫机制或网络问题

**解决方案**：
- 先运行"方案 A"或"方案 C"测试基础功能
- 使用代理或更换网络环境
- 增加等待时间（修改 `shandong.py` 中的 `wait_ms` 参数）

---

## 下一步

### 开发模式

如果您要继续开发 Phase 2（存储集成），可以：

```bash
cd /mnt/oldroot/home/bird/TrendRadar

# 查看当前分支
git branch --show-current  # 应该是 feature/tender-monitoring

# 创建新的测试文件
vim test_phase2_storage.py

# 提交更改
git add .
git commit -m "feat: Phase 2 实现"
```

### 生产部署

完成所有 5 个 Phase 后：

```bash
# 合并到主分支
git checkout master
git merge feature/tender-monitoring

# 启动服务
python3 -m trendradar --config config.yaml
```

---

## 测试检查清单

- [ ] Python 3.8+ 已安装
- [ ] requirements.txt 依赖已安装
- [ ] agent-browser 已安装
- [ ] 模块导入测试通过（方案 A）
- [ ] 基础功能测试通过（方案 C）
- [ ] 验证码服务可访问（方案 B - 可选）
- [ ] 山东省采集测试通过（方案 B - 可选）

---

**最后更新**: 2026-02-19
**Phase 1 状态**: ✅ 完成
**测试状态**: 🟡 基础功能已实现，完整采集待真实环境验证
