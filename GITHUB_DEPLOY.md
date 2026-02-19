# GitHub 部署和 Windows 获取指南

## 重要说明

⚠️ **当前仓库不是您的**：https://github.com/sansan0/TrendRadar.git 是上游开源项目，您无权限直接推送。

- **本地分支**: feature/tender-monitoring（7 个提交）
- **当前状态**: 仅存在本地，未推送到任何远程仓库

---

## 部署方案（请选择一种）

### 方案 A：Fork 上游仓库（推荐，保持同步）

**适用场景**：希望贡献回上游项目，或者保持与 TrendRadar 主线同步。

#### A.1 在 GitHub 上 Fork

1. 访问：https://github.com/sansan0/TrendRadar
2. 点击右上角 **Fork** 按钮
3. 创建到您自己账号下（假设为 `https://github.com/YOUR_USERNAME/TrendRadar`）

#### A.2 添加您的 Fork 为远程仓库

```bash
cd /mnt/oldroot/home/bird/TrendRadar

# 添加您的 Fork 作为新的远程仓库（命名为 myfork）
git remote add myfork https://github.com/YOUR_USERNAME/TrendRadar.git

# 验证远程仓库
git remote -v
# 应显示：
#   origin    https://github.com/sansan0/TrendRadar.git (fetch)
#   origin    https://github.com/sansan0/TrendRadar.git (push)
#   myfork    https://github.com/YOUR_USERNAME/TrendRadar.git (fetch)
#   myfork    https://github.com/YOUR_USERNAME/TrendRadar.git (push)
```

#### A.3 推送分支到您的 Fork

```bash
# 推送 feature/tender-monitoring 分支到 myfork
git push -u myfork feature/tender-monitoring
```

推送完成后访问：`https://github.com/YOUR_USERNAME/TrendRadar/branches`

---

### 方案 B：创建新仓库（推荐，完全独立）

**适用场景**：完全独立的项目，不需要与 TrendRadar 主线同步。

#### B.1 在 GitHub 上创建新仓库

1. 访问：https://github.com/new
2. 仓库名称：`tender-monitor-trendradar`（或其他您喜欢的名称）
3. 描述：基于 TrendRadar 的政府采购招标监控系统
4. 选择 **Public** 或 **Private**
5. **不要** 勾选 "Initialize this repository with a README"
6. 点击 **Create repository**

#### B.2 更改远程仓库指向

```bash
cd /mnt/oldroot/home/bird/TrendRadar

# 移除旧的 origin（指向 sansan0 的仓库）
git remote remove origin

# 添加您的新仓库为 origin
git remote add origin https://github.com/YOUR_USERNAME/tender-monitor-trendradar.git

# 验证
git remote -v
# 应显示：
#   origin    https://github.com/YOUR_USERNAME/tender-monitor-trendradar.git (fetch)
#   origin    https://github.com/YOUR_USERNAME/tender-monitor-trendradar.git (push)
```

#### B.3 推送所有分支

```bash
# 推送 main 分支
git push -u origin main

# 推送 feature/tender-monitoring 分支
git checkout feature/tender-monitoring
git push -u origin feature/tender-monitoring
```

---

### 方案 C：本地传输（无需 Git）

**适用场景**：Windows 机器无网络，或不需要 Git 版本控制。

#### C.1 在 Linux 上打包

```bash
cd /mnt/oldroot/home/bird/TrendRadar

# 切换到 feature/tender-monitoring 分支
git checkout feature/tender-monitoring

# 打包所有必需文件
tar -czf trendradar-tender-windows.tar.gz \
    trendradar/ \
    test_*.py \
    requirements.txt \
    QUICKSTART.md \
    WINDOWS_DEPLOYMENT.md \
    GITHUB_DEPLOY.md \
    README.md

# 压缩包位置
ls -lh trendradar-tender-windows.tar.gz
```

#### C.2 传输到 Windows

使用以下任一方式传输 `trendradar-tender-windows.tar.gz`：
- **SCP/SFTP**：`scp trendradar-tender-windows.tar.gz user@windows-machine:/path/`
- **网络共享**：SMB/CIFS
- **U盘**：直接复制

#### C.3 在 Windows 上解压

使用 7-Zip 或 WinRAR 解压 `.tar.gz` 文件。

---

## Windows 获取代码（对应上述方案）

---

## Windows 获取代码（对应上述方案）

### 对应方案 A（Fork 仓库）

打开 **PowerShell** 或 **Git Bash**：

```powershell
# 1. 选择工作目录
cd C:\Users\YourName\Projects

# 2. 克隆您 Fork 的仓库
git clone https://github.com/YOUR_USERNAME/TrendRadar.git

# 3. 进入目录
cd TrendRadar

# 4. 切换到开发分支
git checkout feature/tender-monitoring

# 5. 验证分支
git branch
# 应该显示：* feature/tender-monitoring
```

### 对应方案 B（新仓库）

```powershell
# 1. 选择工作目录
cd C:\Users\YourName\Projects

# 2. 克隆您的新仓库
git clone https://github.com/YOUR_USERNAME/tender-monitor-trendradar.git

# 3. 进入目录
cd tender-monitor-trendradar

# 4. 切换到开发分支（如果需要）
git checkout feature/tender-monitoring

# 5. 验证分支
git branch
```

### 对应方案 C（本地传输）

1. 将 `trendradar-tender-windows.tar.gz` 复制到 Windows 机器
2. 使用 7-Zip 或 WinRAR 解压
3. 进入解压后的目录：

```powershell
cd C:\path\to\extracted\TrendRadar
dir  # 验证文件存在
```

---

## 步骤 3：Windows 环境配置

### 3.1 安装 Python 依赖

```powershell
# 在 TrendRadar 目录下
pip install -r requirements.txt
```

### 3.2 安装 agent-browser

```powershell
# 使用 npm 全局安装
npm install -g agent-browser

# 验证安装
agent-browser --help
```

### 3.3 验证安装

```powershell
# 测试基础功能
python test_basic.py

# 预期输出：5/5 通过
```

---

## 步骤 4：运行测试

### 4.1 agent-browser 功能测试

```powershell
python test_agent_browser_simple.py
```

预期输出：
```
✅ 所有测试通过！agent-browser 工作正常
🎉 agent-browser 完全正常工作！
   可以继续测试招标网站
```

### 4.2 招标采集测试

#### 广东省测试（推荐，无验证码）

```powershell
python test_tender_guangdong.py
```

#### 山东省测试（需要验证码服务）

**终端 1：启动验证码服务**
```powershell
# 进入验证码服务目录（需要传输或使用原 tender-monitor-demo）
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

## 常见问题

### Q1: git clone 失败（网络问题）

**方案 1：使用 SSH**
```powershell
git clone git@github.com:sansan0/TrendRadar.git
```

**方案 2：使用代理**
```powershell
# 设置 Git 代理（如果有）
git config --global http.proxy http://proxy.example.com:8080
```

**方案 3：下载 ZIP**
1. 访问：https://github.com/sansan0/TrendRadar
2. 点击 "Code" → "Download ZIP"
3. 解压到本地目录

注意：ZIP 方式无法使用 git pull 更新，需要重新下载。

### Q2: git checkout 提示 "分支不存在"

**原因**：远程分支信息未同步

**解决**：
```powershell
git fetch origin
git checkout feature/tender-monitoring
```

### Q3: pip install 失败

**方案 1：使用国内镜像**
```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**方案 2：使用虚拟环境**
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Q4: npm install -g 权限错误

**方案 1：使用管理员权限**
- 右键点击 PowerShell → "以管理员身份运行"
- 再执行 `npm install -g agent-browser`

**方案 2：修改 npm 全局目录**
```powershell
# 设置 npm 全局目录到用户目录
npm config set prefix "%APPDATA%\npm"
npm install -g agent-browser
```

---

## 文件结构检查

克隆/拉取后，应该有以下文件：

```
TrendRadar/
├── trendradar/
│   ├── crawler/
│   │   ├── agent_browser.py          ← 新增
│   │   └── tender/                   ← 新增
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── guangdong.py
│   │       └── shandong.py
│   └── ...（其他 TrendRadar 模块）
├── test_basic.py                     ← 新增
├── test_agent_browser_simple.py      ← 新增
├── test_tender_guangdong.py          ← 新增
├── test_tender_shandong.py           ← 新增
├── WINDOWS_DEPLOYMENT.md             ← 新增
├── GITHUB_DEPLOY.md                  ← 本文档
├── QUICKSTART.md                     ← 新增
├── PHASE1_COMPLETE.md                ← 新增（在 tender-monitor-demo）
└── requirements.txt
```

---

## 验证清单

Windows 环境配置完成后，按顺序验证：

- [ ] Git 克隆/拉取成功
- [ ] 切换到 feature/tender-monitoring 分支
- [ ] 看到新增的文件（agent_browser.py, tender/, test_*.py）
- [ ] Python 依赖安装完成
- [ ] agent-browser 安装完成
- [ ] test_basic.py 通过（5/5）
- [ ] test_agent_browser_simple.py 通过
- [ ] test_tender_guangdong.py 可运行

---

## 后续步骤

测试成功后：

1. **开始开发 Phase 2**
   - 存储集成
   - 调度系统

2. **提交代码**（如果有修改）
   ```powershell
   git add .
   git commit -m "你的提交信息"

   # 根据您选择的方案推送：
   # 方案 A（Fork）：
   git push myfork feature/tender-monitoring

   # 方案 B（新仓库）：
   git push origin feature/tender-monitoring
   ```

3. **创建 Pull Request**（可选）
   - **如果使用方案 A**（Fork），可以向上游项目提交 PR：
     - 访问：https://github.com/sansan0/TrendRadar/pulls
     - 点击 "New pull request"
     - Base: master ← Compare: YOUR_USERNAME:feature/tender-monitoring
     - 描述：Phase 1 招标监控核心模块

   - **如果使用方案 B**（新仓库），可以创建分支间的 PR：
     - 访问：https://github.com/YOUR_USERNAME/tender-monitor-trendradar/pulls
     - Base: main ← Compare: feature/tender-monitoring

---

## 技术支持

如果遇到问题：

1. 查看 WINDOWS_DEPLOYMENT.md（详细部署指南）
2. 查看 QUICKSTART.md（快速开始）
3. 查看 GitHub Issues
4. 检查错误日志

---

## 推荐方案选择指南

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 希望贡献代码给 TrendRadar 社区 | **方案 A（Fork）** | 可以向上游提 PR |
| 独立项目，不需要同步上游 | **方案 B（新仓库）** | 完全自主控制 |
| Windows 无网络，或测试用 | **方案 C（本地传输）** | 无需 Git |
| Windows 有网络，正式开发 | **方案 A 或 B** | 使用 Git 协作 |

---

**最后更新**: 2026-02-20
**原始仓库**: https://github.com/sansan0/TrendRadar.git（上游，只读）
**本地分支**: feature/tender-monitoring（7 commits，仅本地）
**您的仓库**: 请根据上述方案选择创建
