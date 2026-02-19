# Windows 上安装 agent-browser 指南

## 当前状态

✅ Python 依赖已安装
✅ 基础功能测试通过（5/5）
❌ agent-browser 未安装（需要安装）

---

## agent-browser 是什么？

agent-browser 是一个 Node.js CLI 工具，用于浏览器自动化。它使用语义定位器（Accessibility Tree）替代传统的 CSS 选择器，更稳定可靠。

**依赖**：Node.js 16+（需要先安装 Node.js）

---

## 安装步骤

### 步骤 1：检查 Node.js 是否已安装

在 PowerShell 中执行：

```powershell
node --version
npm --version
```

**如果看到版本号**（如 `v18.17.0`, `9.8.1`）：
- ✅ Node.js 已安装，跳到**步骤 2**

**如果提示命令未找到**：
- ❌ 需要先安装 Node.js，继续**步骤 1.1**

---

### 步骤 1.1：安装 Node.js（如果未安装）

#### 方法 A：使用官方安装包（推荐）

1. 访问：https://nodejs.org/
2. 下载 **LTS 版本**（长期支持版，如 v18.x.x）
3. 运行安装包，使用默认设置
4. 安装完成后**重启 PowerShell**
5. 验证：
   ```powershell
   node --version
   npm --version
   ```

#### 方法 B：使用 Chocolatey（命令行安装）

如果您使用 Chocolatey 包管理器：

```powershell
# 以管理员身份运行 PowerShell
choco install nodejs-lts

# 验证
node --version
npm --version
```

#### 方法 C：使用 Winget（Windows 11）

如果您使用 Windows 11 或 Windows 10 较新版本：

```powershell
# 以管理员身份运行 PowerShell
winget install OpenJS.NodeJS.LTS

# 重启 PowerShell
# 验证
node --version
npm --version
```

---

### 步骤 2：安装 agent-browser

#### 方法 A：全局安装（推荐）

**以管理员身份运行 PowerShell**：
1. 右键点击 PowerShell 图标
2. 选择 "以管理员身份运行"
3. 执行：

```powershell
npm install -g agent-browser

# 验证安装
agent-browser --version
```

如果成功，会显示类似：`1.x.x`

#### 方法 B：如果方法 A 权限错误

```powershell
# 修改 npm 全局安装目录到用户目录
npm config set prefix "%APPDATA%\npm"

# 安装 agent-browser
npm install -g agent-browser

# 添加到 PATH（重要！）
# 1. 按 Win + R，输入 sysdm.cpl，回车
# 2. 点击"高级"选项卡 → "环境变量"
# 3. 在"用户变量"中找到 Path，点击"编辑"
# 4. 点击"新建"，添加：%APPDATA%\npm
# 5. 点击"确定"保存

# 重启 PowerShell
# 验证
agent-browser --version
```

#### 方法 C：使用国内镜像（如果安装慢）

```powershell
# 设置淘宝镜像
npm config set registry https://registry.npmmirror.com

# 安装 agent-browser
npm install -g agent-browser

# 验证
agent-browser --version
```

---

### 步骤 3：验证安装

在 PowerShell 中执行：

```powershell
# 检查 agent-browser
agent-browser --version

# 检查浏览器（agent-browser 需要 Chrome 或 Edge）
where chrome
where msedge

# 如果找不到 chrome，但找到了 msedge，没问题
# agent-browser 会自动使用 Edge（Windows 10/11 自带）
```

---

### 步骤 4：重新运行测试

```powershell
# 回到 TrendRadar 目录
cd D:\TrendRadar

# 运行 agent-browser 测试
python test_agent_browser_simple.py
```

预期输出：
```
============================================================
AgentBrowser 基础功能测试
============================================================

测试1: 创建浏览器实例...
  ✓ 实例创建成功: AgentBrowser(session='test_1771522718', headless=True)

测试2: 访问 httpbin.org...
  ✓ 页面加载成功

测试3: 等待页面稳定...
  ✓ 等待完成

测试4: 获取页面快照...
  ✓ 快照获取成功
  ✓ 找到 29 个可交互元素

测试5: 关闭浏览器...
  ✓ 浏览器已关闭

============================================================
✅ 所有测试通过！agent-browser 工作正常
============================================================

============================================================
测试访问中文网站 - 百度
============================================================

访问 https://www.baidu.com ...
  ✓ 百度首页加载成功

获取快照...
  ✓ 找到 33 个可交互元素
  ✓ 找到搜索框: @e5 - 百度一下

✅ 中文网站测试完成

🎉 agent-browser 完全正常工作！
   可以继续测试招标网站
```

---

## 常见问题

### Q1: npm install -g 提示权限错误

**错误信息**：
```
Error: EACCES: permission denied
```

**解决方案**：
1. 以管理员身份运行 PowerShell（推荐）
2. 或者使用方法 B 修改 npm 全局目录

---

### Q2: agent-browser 命令未找到

**错误信息**：
```
'agent-browser' 不是内部或外部命令
```

**原因**：npm 全局目录不在 PATH 中

**解决方案**：
```powershell
# 查找 agent-browser 安装位置
npm config get prefix

# 输出如下路径之一：
# C:\Users\YourName\AppData\Roaming\npm
# C:\Program Files\nodejs

# 将该路径添加到 PATH：
# 1. Win + R → sysdm.cpl → 环境变量
# 2. 编辑 Path，添加上述路径
# 3. 重启 PowerShell
```

---

### Q3: npm install 很慢或失败

**原因**：npm 默认源在国外，速度慢

**解决方案**：
```powershell
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 验证
npm config get registry
# 应显示：https://registry.npmmirror.com/

# 重新安装
npm install -g agent-browser
```

---

### Q4: 找不到 Chrome 浏览器

**错误信息**：
```
Browser not found
```

**解决方案**：
- agent-browser 支持以下浏览器（按优先级）：
  1. Chrome
  2. Chromium
  3. **Edge**（Windows 10/11 自带，无需安装）

- 如果没有 Chrome，agent-browser 会自动使用 Edge
- Edge 在 Windows 10/11 上默认安装，无需额外操作

**验证**：
```powershell
where msedge
# 应显示：C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
```

---

### Q5: 测试时浏览器启动失败

**错误信息**：
```
Failed to launch browser
```

**可能原因**：
1. 防火墙拦截
2. 浏览器路径问题
3. 缺少依赖

**解决方案**：
```powershell
# 1. 暂时禁用防火墙测试
# 2. 使用非无头模式调试（看到浏览器窗口）
# 编辑 test_agent_browser_simple.py，修改：
# headless=False

# 3. 重新安装 Edge（如果 Edge 损坏）
# 访问：https://www.microsoft.com/edge
```

---

## 完整验证清单

安装完成后，逐项检查：

- [ ] `node --version` 显示版本号（如 v18.17.0）
- [ ] `npm --version` 显示版本号（如 9.8.1）
- [ ] `agent-browser --version` 显示版本号（如 1.x.x）
- [ ] `where msedge` 或 `where chrome` 找到浏览器
- [ ] `python test_agent_browser_simple.py` 通过（2个测试）

---

## 下一步

agent-browser 安装成功后：

1. **测试广东省采集**（Linux友好，无验证码）
   ```powershell
   python test_tender_guangdong.py
   ```

2. **测试山东省采集**（需要验证码服务）
   - 需要在 Linux 服务器上启动验证码服务
   - 或者先跳过，等验证码服务部署完成

---

## 快速诊断命令

如果遇到问题，运行以下命令并提供输出：

```powershell
# 1. Node.js 版本
node --version
npm --version

# 2. npm 配置
npm config get prefix
npm config get registry

# 3. agent-browser
agent-browser --version
where agent-browser

# 4. 浏览器
where chrome
where msedge

# 5. PATH 环境变量
$env:PATH -split ';' | Select-String npm
```

---

**最后更新**: 2026-02-20
**适用平台**: Windows 10/11 x64
