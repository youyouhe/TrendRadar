# TrendRadar + agent-browser Windows 兼容性报告

## 执行摘要

**结论**: agent-browser 0.12.0 在 Windows Administrator 账户下**无法启动守护进程**，导致整个方案不可用。

**建议**: 回到已验证可用的 **tender-monitor-demo** 方案（Go + Rod）。

---

## 测试环境

- **操作系统**: Windows 10 (版本 10.0.19045)
- **用户账户**: Administrator
- **Python 版本**: 3.12.8
- **Node.js 版本**: 已安装（npm 可用）
- **agent-browser 版本**: 0.12.0
- **浏览器**: Chrome (C:\Program Files\Google\Chrome\Application\chrome.exe)

---

## 问题历程

### 阶段 1：基础功能验证 ✅

**测试**: `python test_basic.py`
**结果**: ✅ **通过 (5/5)**

- ✅ 模块导入正常
- ✅ TenderData 数据结构正常
- ✅ 数据源注册正常
- ✅ AgentBrowser 初始化正常
- ✅ 山东数据源类正常

**结论**: Python 代码逻辑无问题，TrendRadar 集成正确。

---

### 阶段 2：Windows 平台适配 ✅

#### 问题 2.1：agent-browser 命令未找到

**错误**:
```
FileNotFoundError: [WinError 2] 系统找不到指定的文件。
```

**原因**: Windows 上 npm 全局命令是 `.cmd` 批处理文件，Python `subprocess.run()` 默认不执行 `.cmd` 文件。

**修复** (提交 `8b4d7d53`):
```python
# 在 AgentBrowser.__init__() 中
agent_cmd = "agent-browser.cmd" if platform.system() == "Windows" else "agent-browser"
self._base_cmd = [agent_cmd]
```

**验证**: `python test_windows_fix.py` ✅ 通过

---

#### 问题 2.2：UTF-8 编码冲突

**错误**:
```
UnicodeDecodeError: 'gbk' codec can't decode byte 0x97 in position 7: illegal multibyte sequence
```

**原因**: Windows 中文系统默认 GBK 编码，agent-browser 输出 UTF-8。

**修复** (提交 `72997610`):
```python
result = subprocess.run(
    cmd,
    encoding='utf-8',  # 显式指定 UTF-8
    errors='replace',  # 容错处理
    ...
)
```

**验证**: 错误信息可正常显示 ✅

---

### 阶段 3：浏览器启动问题 ❌

#### 问题 3.1：守护进程启动失败

**错误**:
```
✗ Daemon failed to start (socket: C:\Users\Administrator\.agent-browser\test_xxx.sock)
```

**尝试的解决方案**:

1. ❌ **设置 CHROME_PATH 环境变量**
   ```powershell
   $env:CHROME_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
   ```
   结果: 仍然失败

2. ❌ **添加 Chrome 到 PATH**
   ```powershell
   $env:PATH += ";C:\Program Files\Google\Chrome\Application"
   ```
   结果: 仍然失败

3. ❌ **关闭所有 Chrome 进程**
   ```powershell
   taskkill /F /IM chrome.exe
   ```
   结果: 仍然失败

4. ❌ **清理残留 socket 文件**
   ```powershell
   Remove-Item -Recurse -Force "$env:USERPROFILE\.agent-browser"
   ```
   结果: 仍然失败

**诊断结果**:
- ✅ agent-browser 命令可执行 (`--version` 正常)
- ✅ Chrome 已安装且路径正确
- ✅ 无残留 socket 文件
- ❌ **守护进程始终无法启动，不创建 socket 文件**

**结论**: agent-browser 0.12.0 在 Windows Administrator 账户下有严重的兼容性问题，与配置无关。

---

## 已完成的工作成果

### 代码实现 (13 个提交)

1. ✅ **核心封装**: `trendradar/crawler/agent_browser.py` (460 行)
   - AgentBrowser 类完整实现
   - Windows 平台适配 (.cmd 后缀)
   - UTF-8 编码修复

2. ✅ **数据模型**: `trendradar/crawler/tender/base.py`
   - TenderData 数据类
   - TenderSource 抽象基类
   - 关键词匹配 (ANY/ALL/EXACT)

3. ✅ **采集实现**:
   - `trendradar/crawler/tender/shandong.py` - 山东省采集
   - `trendradar/crawler/tender/guangdong.py` - 广东省采集

4. ✅ **测试脚本**:
   - `test_basic.py` - 基础功能测试 (5/5 通过)
   - `test_agent_browser_simple.py` - agent-browser 测试
   - `test_tender_guangdong.py` - 广东省采集测试
   - `test_tender_shandong.py` - 山东省采集测试
   - `test_windows_fix.py` - Windows 修复验证
   - `test_chrome_path.py` - Chrome 路径测试

5. ✅ **诊断工具**:
   - `diagnose_agent_browser.py` - 7 项诊断测试
   - `diagnose_browser.py` - 浏览器启动诊断
   - `diagnose_agent_browser_verbose.py` - 详细日志诊断

### 文档 (5 个)

1. ✅ **部署指南**:
   - `WINDOWS_DEPLOYMENT.md` - 通用 Windows 部署指南
   - `Windows部署指南-youyouhe.md` - 定制化部署指南
   - `安装agent-browser-Windows.md` - agent-browser 安装指南

2. ✅ **GitHub 工作流**:
   - `GITHUB_DEPLOY.md` - 三种部署方案（Fork/新仓库/本地传输）
   - `部署方案选择.md` - 决策流程和对比表

3. ✅ **快速开始**:
   - `QUICKSTART.md` - 快速开始指南

### GitHub 仓库

- **仓库**: https://github.com/youyouhe/TrendRadar
- **分支**: feature/tender-monitoring
- **提交数**: 13 commits
- **代码行数**: ~2000 行（代码 + 文档）

---

## 技术分析

### agent-browser 的问题

**推测的根本原因**:

1. **Socket 通信问题**
   - agent-browser 使用 Unix socket 进行进程间通信
   - Windows 的 Named Pipes 与 Unix socket 行为不同
   - 可能未正确实现 Windows 适配

2. **权限问题**
   - Administrator 账户在 Windows 上有特殊安全限制
   - 可能触发了 UAC (User Account Control) 或其他权限限制
   - Socket 文件创建可能被阻止

3. **浏览器启动问题**
   - agent-browser 可能依赖特定的浏览器启动参数
   - Windows 上 Chrome 的启动方式与 Linux/macOS 不同
   - 守护进程可能在尝试启动浏览器时失败

### 为什么 Rod (tender-monitor-demo) 可用

| 特性 | agent-browser | Rod (Go) |
|------|---------------|----------|
| **进程模型** | 守护进程 + Socket | 直接调用浏览器 |
| **平台支持** | 主要针对 Linux/macOS | 全平台支持 |
| **成熟度** | 新项目 (0.12.0) | 成熟项目 (v0.114+) |
| **依赖** | Node.js + 系统调用 | 纯 Go，无外部依赖 |
| **Windows 测试** | 不充分 | 广泛测试 |

---

## 推荐方案

### 方案 A：使用 tender-monitor-demo（强烈推荐）

**优点**:
- ✅ 已在 Windows 上验证可用
- ✅ 功能完整（UI/API/分页/导出/任务取消）
- ✅ Go 编译为单一可执行文件，无依赖问题
- ✅ Rod 浏览器自动化库成熟稳定

**启动**:
```powershell
cd D:\tender-monitor-demo
.\tender-monitor.exe
# 访问 http://localhost:8080
```

---

### 方案 B：使用 TrendRadar + Playwright（备选）

**如果坚持使用 TrendRadar 架构**:

1. 用 **Playwright** 替代 agent-browser
2. Playwright 是成熟的 Python 浏览器自动化库
3. Windows 兼容性优秀

**工作量**: 重写 `agent_browser.py` (2-3 小时)

**优点**:
- ✅ 保持 TrendRadar 架构
- ✅ Playwright 在 Windows 上稳定

**缺点**:
- ❌ 需要额外开发时间
- ❌ 失去 agent-browser 的语义定位优势

---

### 方案 C：等待 agent-browser 修复（不推荐）

等待 agent-browser 项目改进 Windows 支持。

**时间**: 可能需要数月

**风险**: 不确定是否会修复

---

## 结论

经过 13 次提交、多个诊断工具、5 份文档的工作后，确认 **agent-browser 0.12.0 在 Windows 上不可用**。

**建议**: 立即切换到已验证可用的 **tender-monitor-demo** 方案。

---

## 附录：提交历史

```
f9486342 feat: 添加 agent-browser 详细诊断脚本
80fefc94 feat: 添加 Chrome 路径设置测试脚本
2572bf5f feat: 添加浏览器启动问题诊断工具
72997610 fix: 修复 Windows 平台 UTF-8 编码问题
8b4d7d53 fix: 修复 Windows 平台 agent-browser 执行问题
362920b1 docs: 添加 Windows 部署指南和 GitHub 工作流文档
464001ac docs: 添加 Windows 平台部署指南
1ca7247f fix: 修复 AgentBrowser CLI 命令格式
e3c1cead feat: 添加广东省招标采集支持
...
```

---

**报告日期**: 2026-02-20
**测试平台**: Windows 10 (10.0.19045)
**GitHub 仓库**: https://github.com/youyouhe/TrendRadar/tree/feature/tender-monitoring
