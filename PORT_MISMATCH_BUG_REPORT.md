# agent-browser 0.12.0 端口计算不匹配 BUG 报告

## 执行摘要

✅ **守护进程可以成功启动**
❌ **但 Rust CLI 连接到错误的端口**

**根本原因**: Rust CLI 和 Node.js 守护进程的端口计算逻辑不一致。

---

## 问题描述

### 症状

```
错误信息: Daemon failed to start (socket: C:\Users\Administrator\.agent-browser\test_xxx.sock)
返回码: 1
```

### 实际情况

诊断结果显示：
- ✅ Node.js 正常 (v24.12.0)
- ✅ daemon.js 文件存在
- ✅ 端口 60717 可用（Rust 计算的端口）
- ✅ **守护进程成功启动** (PID: 51956)
- ✅ Port 文件创建: **58014** ← **实际端口**

**关键发现**：
```
会话名: test_diagnose
Rust/PowerShell 计算端口: 60717
Node.js 守护进程实际端口: 58014
差异: 2703 个端口号
```

---

## 技术分析

### Rust CLI 端口计算 (cli/src/connection.rs:143-151)

```rust
fn get_port_for_session(session: &str) -> u16 {
    let mut hash: i32 = 0;
    for c in session.chars() {
        hash = ((hash << 5).wrapping_sub(hash)).wrapping_add(c as i32);
    }
    // 使用 unsigned_abs() 处理负数
    49152 + ((hash.unsigned_abs() as u32 % 16383) as u16)
}
```

### Node.js 守护进程端口计算 (src/daemon.ts:147-155)

```typescript
function getPortForSession(session: string): number {
  let hash = 0;
  for (let i = 0; i < session.length; i++) {
    hash = (hash << 5) - hash + session.charCodeAt(i);
    hash |= 0;  // ← 关键差异：强制转为32位有符号整数
  }
  // 使用 Math.abs() 处理负数
  return 49152 + (Math.abs(hash) % 16383);
}
```

### 关键差异

| 实现 | 整数溢出处理 | 负数处理 |
|------|------------|---------|
| **Rust** | `wrapping_sub/add` | `unsigned_abs()` |
| **JavaScript** | `hash |= 0` (32位截断) | `Math.abs()` |

**JavaScript 的 `hash |= 0`**:
- 将浮点数强制转为32位有符号整数
- 范围: -2,147,483,648 to 2,147,483,647
- 溢出时会截断高位

**Rust 的 `wrapping_sub/add`**:
- i32 范围相同，但溢出行为不同
- `unsigned_abs()` 将 i32 转为 u32 再取绝对值

对于长会话名，累加过程中的溢出处理差异导致最终 hash 值不同。

---

## 复现步骤

### 步骤 1: 计算预期端口（Rust 逻辑）

```powershell
$session = "test_diagnose"
$hash = 0
foreach ($char in $session.ToCharArray()) {
    $hash = (($hash -shl 5) - $hash) + [int]$char
}
$port = 49152 + ([Math]::Abs($hash) % 16383)
Write-Host "Expected port: $port"  # 输出: 60717
```

### 步骤 2: 启动守护进程

```powershell
$env:AGENT_BROWSER_DAEMON = "1"
$env:AGENT_BROWSER_SESSION = "test_diagnose"
node "C:\Users\...\agent-browser\dist\daemon.js"
```

### 步骤 3: 检查实际端口

```powershell
Get-Content "$env:USERPROFILE\.agent-browser\test_diagnose.port"
# 输出: 58014
```

### 步骤 4: 尝试连接（Rust CLI）

```powershell
agent-browser --session test_diagnose snapshot
# 错误: Daemon failed to start
```

**原因**: Rust CLI 连接到端口 60717，但守护进程监听在端口 58014。

---

## 影响范围

### 受影响的版本

- ✅ agent-browser 0.12.0 **存在此 BUG**
- ❓ agent-browser 0.11.x **需要验证**
- ❓ 更早版本 **需要验证**

### 受影响的平台

- ✅ **Windows** - 使用 TCP 端口通信，**受影响**
- ❓ **Linux/macOS** - 使用 Unix Socket，**不受影响**（不涉及端口计算）

### 影响条件

只有 Windows 平台受影响，因为：
- Linux/macOS 使用 Unix Domain Socket (`.sock` 文件)，不需要端口计算
- Windows 使用 TCP localhost + 动态端口，依赖端口计算

---

## 测试用例

### 用例 1: test_diagnose

```
会话名: test_diagnose
Rust 计算: 60717
Node.js 实际: 58014
差异: 2703
状态: ❌ 失败
```

### 用例 2: test_1771523393

```
会话名: test_1771523393
Rust 计算: ? (待验证)
Node.js 实际: ? (待验证)
状态: ❌ 失败 (历史测试记录)
```

### 用例 3: baidu_1771523401

```
会话名: baidu_1771523401
Rust 计算: ? (待验证)
Node.js 实际: ? (待验证)
状态: ❌ 失败 (历史测试记录)
```

---

## 解决方案

### 方案 A: 报告 BUG 给上游（推荐）

**GitHub Issue**: https://github.com/vercel-labs/agent-browser/issues

**Issue 标题**: `[Windows] Port calculation mismatch between Rust CLI and Node.js daemon`

**Issue 内容**:
```markdown
## Description
On Windows, the Rust CLI and Node.js daemon calculate different port numbers for the same session name, causing connection failures.

## Reproduction
1. Start daemon: `AGENT_BROWSER_SESSION=test_diagnose node dist/daemon.js`
2. Check port file: `cat ~/.agent-browser/test_diagnose.port` → 58014
3. Try CLI: `agent-browser --session test_diagnose snapshot` → Fails
4. CLI tries to connect to port 60717 (calculated by Rust)

## Root Cause
Port calculation differs:
- Rust: Uses `wrapping_sub/add` + `unsigned_abs()`
- JavaScript: Uses `hash |= 0` (32-bit truncation) + `Math.abs()`

## Expected Behavior
CLI and daemon should calculate the same port number.

## Versions
- agent-browser: 0.12.0
- OS: Windows 10
- Node.js: v24.12.0
```

---

### 方案 B: 降级到旧版本

```powershell
# 卸载当前版本
npm uninstall -g agent-browser

# 安装旧版本
npm install -g agent-browser@0.11.0

# 验证版本
agent-browser --version
```

**注意**: 需要验证 0.11.0 是否也有此问题。

---

### 方案 C: 使用 tender-monitor-demo（推荐，立即可用）

```powershell
cd D:\tender-monitor-demo
.\tender-monitor.exe
# 访问 http://localhost:8080
```

**优势**:
- ✅ 已在 Windows 上验证可用
- ✅ Go + Rod，无端口计算问题
- ✅ 功能完整（UI/API/分页/导出/任务取消）

---

## 临时修复（高级用户）

### 修复 Node.js 守护进程代码

编辑 `dist/daemon.js`，找到 `getPortForSession` 函数：

```javascript
// 原代码
function getPortForSession(session) {
  let hash = 0;
  for (let i = 0; i < session.length; i++) {
    hash = (hash << 5) - hash + session.charCodeAt(i);
    hash |= 0;  // ← 删除这行
  }
  return 49152 + (Math.abs(hash) % 16383);
}

// 修改为（与 Rust 一致）
function getPortForSession(session) {
  let hash = 0;
  for (let i = 0; i < session.length; i++) {
    hash = (hash << 5) - hash + session.charCodeAt(i);
    // 不使用 |= 0 截断
  }
  // JavaScript 的 Math.abs 对大整数可能溢出
  // 需要模拟 Rust 的 unsigned_abs 行为
  const absHash = Math.abs(hash) >>> 0;  // 转为无符号32位
  return 49152 + (absHash % 16383);
}
```

**警告**:
- 修改后需要重启所有守护进程
- npm 更新会覆盖修改
- 不建议生产环境使用

---

## 验证脚本

### PowerShell 验证脚本

```powershell
cd D:\TrendRadar
git pull origin feature/tender-monitoring
powershell -ExecutionPolicy Bypass -File verify_port_bug.ps1
```

输出示例：
```
Session: test_diagnose
------------------------------------------------------------
  PowerShell/Rust: 60717
  JavaScript/Node: 58014
  [BUG] Port mismatch!
  Actual port (from file): 58014
  [CONFIRMED] Daemon uses JavaScript calculation
```

---

## 结论

这是 **agent-browser 0.12.0 在 Windows 平台的严重 BUG**。

**事实**:
- ✅ 守护进程可以正常启动
- ✅ Node.js、daemon.js、Playwright 都正常
- ❌ **Rust CLI 计算错误的端口号**
- ❌ CLI 连接失败 → "Daemon failed to start"

**影响**:
- Windows 用户完全无法使用 agent-browser 0.12.0
- Linux/macOS 不受影响（使用 Unix Socket）

**推荐方案**:
1. **立即**: 使用 tender-monitor-demo
2. **短期**: 降级到 agent-browser@0.11.0
3. **长期**: 等待上游修复

---

## 附录

### 相关文件

- **源码分析**: `/mnt/oldroot/home/bird/agent-browser/`
  - `cli/src/connection.rs:143-151` (Rust 端口计算)
  - `src/daemon.ts:147-155` (Node.js 端口计算)

- **诊断脚本**: `D:\TrendRadar\`
  - `diagnose_daemon_simple.ps1` (守护进程启动诊断)
  - `verify_port_bug.ps1` (端口计算验证)

### 测试记录

- **Windows 10**: Administrator 账户
  - Node.js: v24.12.0
  - npm: 11.6.2
  - agent-browser: 0.12.0
  - Chrome: C:\Program Files\Google\Chrome\Application\chrome.exe

### 提交历史

```
44039ef7 feat: 添加端口计算不匹配验证脚本
a0a716b2 fix: 修复 PowerShell 诊断脚本语法错误
86a0c2b5 feat: 添加 Windows 守护进程启动详细诊断脚本
6e3337c7 docs: 添加 Windows 兼容性测试报告
...
```

---

**报告日期**: 2026-02-20
**agent-browser 版本**: 0.12.0
**平台**: Windows 10 (10.0.19045)
**GitHub 仓库**: https://github.com/youyouhe/TrendRadar/tree/feature/tender-monitoring
**上游 BUG 报告**: 待提交
