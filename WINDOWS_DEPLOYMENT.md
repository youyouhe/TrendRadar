# Windows 平台部署指南

## 系统要求

- **操作系统**: Windows 10/11 (x64)
- **Python**: 3.8+
- **Node.js**: 16+ (用于安装 agent-browser)
- **Git**: 用于克隆代码

---

## 快速开始

### 1. 安装依赖

#### 安装 Python 依赖

```powershell
# 在项目目录下
cd C:\path\to\TrendRadar

# 安装 Python 依赖
pip install -r requirements.txt
```

#### 安装 agent-browser

```powershell
# 使用 npm 全局安装
npm install -g agent-browser

# 验证安装
agent-browser --help
```

### 2. 测试基础功能

```powershell
# 测试模块导入和数据结构
python test_basic.py

# 测试 agent-browser 功能
python test_agent_browser_simple.py
```

### 3. 测试招标采集

#### 广东省（推荐，无验证码）

```powershell
python test_tender_guangdong.py
```

#### 山东省（需要验证码服务）

**终端 1：启动验证码服务**
```powershell
cd ..\tender-monitor-demo\captcha-service
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 5000
```

**终端 2：运行测试**
```powershell
cd C:\path\to\TrendRadar
python test_tender_shandong.py
```

---

## Windows 特定说明

### 1. PowerShell 执行策略

如果遇到脚本执行限制：

```powershell
# 查看当前策略
Get-ExecutionPolicy

# 临时允许脚本执行（推荐）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 或者永久允许（需要管理员权限）
Set-ExecutionPolicy RemoteSigned
```

### 2. 路径分隔符

Windows 使用反斜杠 `\`，但 Python 代码中已处理兼容性，无需修改。

### 3. 浏览器兼容性

Windows 上的 agent-browser 会自动使用：
- Chromium（如果已安装）
- Chrome（如果已安装）
- Edge（Windows 10/11 自带）

如果遇到浏览器问题，可以手动指定：

```python
browser = AgentBrowser(
    session_name="test",
    headless=True
)
# agent-browser 会自动检测可用浏览器
```

---

## 文件传输（Linux → Windows）

### 方案 1：Git（推荐）

```powershell
# 在 Windows 上克隆仓库
git clone https://github.com/your-repo/TrendRadar.git
cd TrendRadar
git checkout feature/tender-monitoring
```

### 方案 2：直接打包

在 Linux 上：
```bash
cd /mnt/oldroot/home/bird/TrendRadar
tar -czf trendradar-windows.tar.gz \
    trendradar/ \
    test_*.py \
    requirements.txt \
    QUICKSTART.md \
    WINDOWS_DEPLOYMENT.md
```

传输到 Windows 后解压。

### 方案 3：网络共享

使用 SMB/FTP/SCP 等工具传输整个目录。

---

## 常见问题

### Q1: npm install -g agent-browser 失败

**原因**: 权限不足或网络问题

**解决方案**:
```powershell
# 使用管理员权限运行 PowerShell
# 或者使用淘宝镜像
npm install -g agent-browser --registry=https://registry.npmmirror.com
```

### Q2: Python 找不到模块

**原因**: 依赖未安装或虚拟环境未激活

**解决方案**:
```powershell
# 重新安装依赖
pip install -r requirements.txt

# 或使用虚拟环境
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Q3: agent-browser 启动浏览器失败

**原因**: 浏览器未安装或路径问题

**解决方案**:
```powershell
# 检查浏览器
where chrome
where msedge

# 如果没有 Chrome，安装 Chrome 或使用 Edge
# agent-browser 会自动检测
```

### Q4: 连接超时或 ERR_CONNECTION_RESET

**原因**:
- 网络问题
- 防火墙拦截
- 目标网站的反爬虫机制

**解决方案**:
```powershell
# 1. 检查网络连接
ping gdgpo.czt.gd.gov.cn

# 2. 暂时禁用防火墙测试
# 3. 使用代理（如果网站有地域限制）

# 4. 增加超时时间（在代码中）
browser = AgentBrowser(
    session_name="test",
    headless=True,
    timeout=60000  # 60秒
)
```

### Q5: 中文显示乱码

**原因**: 终端编码问题

**解决方案**:
```powershell
# PowerShell 设置 UTF-8 编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001

# 或使用 Windows Terminal（推荐）
```

---

## 性能优化

### 1. 使用非无头模式调试

测试时可以看到浏览器窗口：

```python
browser = AgentBrowser(
    session_name="test",
    headless=False  # 显示浏览器窗口
)
```

### 2. 并发采集

Windows 支持多进程，可以并行采集多个省份：

```python
from concurrent.futures import ThreadPoolExecutor

provinces = ["guangdong", "shandong", "zhejiang"]
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(collect_province, provinces)
```

### 3. 缓存会话

复用浏览器会话可以提高速度：

```python
# 使用相同的 session_name 复用浏览器实例
browser = AgentBrowser(session_name="persistent")
# 第一次慢，后续快
```

---

## 目录结构

```
TrendRadar/
├── trendradar/
│   ├── crawler/
│   │   ├── agent_browser.py      # AgentBrowser 封装
│   │   └── tender/               # 招标采集模块
│   │       ├── base.py           # 抽象基类
│   │       ├── guangdong.py      # 广东省实现
│   │       └── shandong.py       # 山东省实现
│   ├── storage/                  # 存储模块（TrendRadar）
│   ├── notification/             # 通知模块（TrendRadar）
│   └── ai/                       # AI 分析（TrendRadar）
├── test_basic.py                 # 基础功能测试
├── test_agent_browser_simple.py  # agent-browser 测试
├── test_tender_guangdong.py      # 广东省测试
├── test_tender_shandong.py       # 山东省测试
├── requirements.txt              # Python 依赖
├── QUICKSTART.md                 # 快速开始指南
└── WINDOWS_DEPLOYMENT.md         # 本文档
```

---

## 测试检查清单

- [ ] Python 3.8+ 已安装
- [ ] Node.js 16+ 已安装
- [ ] agent-browser 安装成功
- [ ] Python 依赖安装完成
- [ ] test_basic.py 通过（5/5）
- [ ] test_agent_browser_simple.py 通过
- [ ] test_tender_guangdong.py 可运行（需要网络）

---

## 下一步

测试成功后，可以：

1. **集成存储**: 使用 TrendRadar 的 StorageManager 保存数据
2. **定时采集**: 使用 TrendRadar 的 Scheduler 定时运行
3. **通知推送**: 集成飞书/钉钉通知
4. **AI 分析**: 使用 LiteLLM 分析招标内容

详见项目文档：
- Phase 2: 存储和调度集成
- Phase 3: Web UI 和 API
- Phase 4: 关键词匹配和通知
- Phase 5: AI 分析和报告

---

## 技术支持

如果遇到问题：

1. 查看错误日志
2. 检查 GitHub Issues
3. 参考 QUICKSTART.md
4. 查看完整文档 PHASE1_COMPLETE.md

---

**最后更新**: 2026-02-20
**测试平台**: Windows 10/11 x64
**agent-browser 版本**: 支持 Windows 原生运行
