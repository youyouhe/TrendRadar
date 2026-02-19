# Windows 部署指南 - youyouhe/TrendRadar

## ✅ 推送成功

您的 `feature/tender-monitoring` 分支已成功推送到：
- **GitHub 仓库**: https://github.com/youyouhe/TrendRadar
- **分支**: feature/tender-monitoring
- **提交数**: 7 commits

---

## Windows 上获取代码（三步完成）

### 步骤 1：打开 PowerShell 或 Git Bash

在 Windows 上打开终端：
- **PowerShell**: 按 `Win + X`，选择 "Windows PowerShell"
- **Git Bash**: 如果已安装 Git for Windows，右键桌面选择 "Git Bash Here"

### 步骤 2：克隆仓库

```powershell
# 选择工作目录（例如）
cd C:\Users\YourName\Projects
# 或者
cd D:\Work

# 克隆您的仓库
git clone https://github.com/youyouhe/TrendRadar.git

# 进入目录
cd TrendRadar
```

### 步骤 3：切换到开发分支

```powershell
# 切换到 feature/tender-monitoring 分支
git checkout feature/tender-monitoring

# 验证分支
git branch
# 应显示：* feature/tender-monitoring

# 查看文件
dir
# 应看到：trendradar/, test_*.py, requirements.txt 等
```

---

## 安装依赖

### 1. 安装 Python 依赖

```powershell
# 确保在 TrendRadar 目录下
cd C:\Users\YourName\Projects\TrendRadar

# 安装依赖（推荐使用虚拟环境）
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

如果下载慢，使用国内镜像：
```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 安装 agent-browser

```powershell
# 使用管理员权限运行 PowerShell
npm install -g agent-browser

# 验证安装
agent-browser --version
```

如果权限不足：
```powershell
# 方法1：使用管理员权限运行 PowerShell（推荐）
# 右键点击 PowerShell → "以管理员身份运行"

# 方法2：修改 npm 全局目录
npm config set prefix "%APPDATA%\npm"
npm install -g agent-browser
```

---

## 运行测试

### 测试 1：基础功能测试（无需网络）

```powershell
python test_basic.py
```

预期输出：
```
✓ 测试1：模块导入
✓ 测试2：数据结构创建
✓ 测试3：关键词匹配（any模式）
✓ 测试4：关键词匹配（all模式）
✓ 测试5：关键词匹配（exact模式）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 所有测试通过 (5/5)
```

### 测试 2：agent-browser 功能测试

```powershell
python test_agent_browser_simple.py
```

预期输出：
```
✅ 所有测试通过！agent-browser 工作正常
🎉 agent-browser 完全正常工作！
   可以继续测试招标网站
```

### 测试 3：广东省招标采集测试

```powershell
python test_tender_guangdong.py
```

这个测试会实际访问广东省政府采购网，采集"软件开发"和"信息化"关键词的招标信息。

---

## 文件结构检查

克隆后，应该有以下文件：

```
TrendRadar/
├── trendradar/
│   ├── crawler/
│   │   ├── agent_browser.py          ← AgentBrowser 封装
│   │   └── tender/                   ← 招标采集模块
│   │       ├── __init__.py
│   │       ├── base.py               ← 抽象基类
│   │       ├── guangdong.py          ← 广东省实现
│   │       └── shandong.py           ← 山东省实现
│   └── ...（其他 TrendRadar 模块）
├── test_basic.py                     ← 基础功能测试
├── test_agent_browser_simple.py      ← agent-browser 测试
├── test_tender_guangdong.py          ← 广东省测试
├── test_tender_shandong.py           ← 山东省测试（需验证码服务）
├── requirements.txt                  ← Python 依赖
├── WINDOWS_DEPLOYMENT.md             ← Windows 部署指南
├── QUICKSTART.md                     ← 快速开始
├── 部署方案选择.md                    ← 部署方案对比
└── Windows部署指南-youyouhe.md       ← 本文档
```

---

## 常见问题

### Q1: git clone 很慢或失败

**方法1：使用 SSH（如果配置了 SSH 密钥）**
```powershell
git clone git@github.com:youyouhe/TrendRadar.git
```

**方法2：使用代理（如果有）**
```powershell
git config --global http.proxy http://proxy.example.com:8080
git config --global https.proxy https://proxy.example.com:8080
```

**方法3：下载 ZIP**
1. 访问：https://github.com/youyouhe/TrendRadar
2. 点击 "Code" → "Download ZIP"
3. 解压到本地目录
4. 注意：ZIP 方式无法使用 `git pull` 更新

### Q2: npm install -g 权限错误

**解决方案1：使用管理员权限（推荐）**
- 右键点击 PowerShell → "以管理员身份运行"
- 再执行 `npm install -g agent-browser`

**解决方案2：修改 npm 全局目录**
```powershell
npm config set prefix "%APPDATA%\npm"
npm install -g agent-browser

# 添加到 PATH（如果需要）
# 控制面板 → 系统 → 高级系统设置 → 环境变量
# 在 Path 中添加：%APPDATA%\npm
```

### Q3: Python 找不到模块

**原因**：虚拟环境未激活或依赖未安装

**解决方案**：
```powershell
# 激活虚拟环境
.\venv\Scripts\activate

# 重新安装依赖
pip install -r requirements.txt

# 验证安装
pip list | findstr requests
```

### Q4: 中文显示乱码

**解决方案**：
```powershell
# PowerShell 设置 UTF-8 编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
```

或者使用 **Windows Terminal**（推荐，支持 UTF-8）：
- 从 Microsoft Store 安装 "Windows Terminal"
- 默认支持中文显示

### Q5: agent-browser 启动浏览器失败

**原因**：浏览器未安装或路径问题

**解决方案**：
```powershell
# 检查浏览器
where chrome
where msedge

# agent-browser 会自动检测：
# 1. Chrome（优先）
# 2. Edge（Windows 10/11 自带）
# 3. Chromium

# 如果没有 Chrome，可以使用 Edge（无需额外安装）
```

---

## 验证清单

完成部署后，按顺序验证：

- [ ] Git 克隆成功
- [ ] 切换到 `feature/tender-monitoring` 分支
- [ ] 看到新增的文件（`agent_browser.py`, `tender/`, `test_*.py`）
- [ ] Python 虚拟环境创建并激活
- [ ] `pip install -r requirements.txt` 成功
- [ ] `agent-browser --version` 有输出
- [ ] `python test_basic.py` 通过（5/5）
- [ ] `python test_agent_browser_simple.py` 通过
- [ ] `python test_tender_guangdong.py` 可运行（需要网络）

---

## 后续开发

### 提交代码到您的仓库

```powershell
# 修改代码后
git add .
git commit -m "描述您的修改"

# 推送到您的 Fork
git push myfork feature/tender-monitoring

# 或者推送到 origin（如果已设置）
git push origin feature/tender-monitoring
```

### 同步上游更新（可选）

如果想要获取 `sansan0/TrendRadar` 的最新更新：

```powershell
# 拉取上游更新
git fetch origin

# 合并到当前分支
git merge origin/master

# 解决冲突（如果有）
# 然后推送到您的 Fork
git push myfork feature/tender-monitoring
```

### 创建 Pull Request（可选）

如果想向上游贡献代码：
1. 访问：https://github.com/sansan0/TrendRadar/pulls
2. 点击 "New pull request"
3. 点击 "compare across forks"
4. Base: `sansan0/TrendRadar:master` ← Compare: `youyouhe/TrendRadar:feature/tender-monitoring`
5. 填写 PR 描述，提交

---

## 快速链接

- **您的 GitHub 仓库**: https://github.com/youyouhe/TrendRadar
- **开发分支**: https://github.com/youyouhe/TrendRadar/tree/feature/tender-monitoring
- **上游项目**: https://github.com/sansan0/TrendRadar
- **问题反馈**: https://github.com/youyouhe/TrendRadar/issues

---

## 技术支持

如果遇到问题：
1. 查看本文档的"常见问题"部分
2. 查看 `WINDOWS_DEPLOYMENT.md`（详细部署指南）
3. 查看 `QUICKSTART.md`（快速开始）
4. 在您的仓库创建 Issue

---

**最后更新**: 2026-02-20
**您的仓库**: https://github.com/youyouhe/TrendRadar
**开发分支**: feature/tender-monitoring（7 commits）
**状态**: ✅ 已推送到远程
