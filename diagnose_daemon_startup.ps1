# Windows agent-browser 守护进程启动诊断脚本
# 用于诊断 "Daemon failed to start" 问题

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "agent-browser 守护进程启动详细诊断" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 测试 1: 检查 Node.js
Write-Host "测试 1: 检查 Node.js" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------"
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor Green
    Write-Host "  ✓ npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js 未安装或不在 PATH 中" -ForegroundColor Red
    Write-Host "    这是守护进程启动失败的主要原因" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 测试 2: 检查 daemon.js
Write-Host "测试 2: 检查 daemon.js 文件" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------"
$npmPrefix = npm prefix -g
$daemonPath = Join-Path $npmPrefix "node_modules\agent-browser\dist\daemon.js"
if (Test-Path $daemonPath) {
    Write-Host "  ✓ daemon.js 找到: $daemonPath" -ForegroundColor Green
} else {
    Write-Host "  ✗ daemon.js 未找到: $daemonPath" -ForegroundColor Red
    Write-Host "    尝试其他位置..." -ForegroundColor Yellow

    $altPaths = @(
        (Join-Path $npmPrefix "node_modules\agent-browser\daemon.js"),
        ".\dist\daemon.js",
        ".\daemon.js"
    )

    $found = $false
    foreach ($path in $altPaths) {
        if (Test-Path $path) {
            Write-Host "  ✓ 在备用位置找到: $path" -ForegroundColor Green
            $daemonPath = $path
            $found = $true
            break
        }
    }

    if (-not $found) {
        Write-Host "  ✗ 所有位置都未找到 daemon.js" -ForegroundColor Red
        Write-Host "    agent-browser 可能未正确安装" -ForegroundColor Red
    }
}
Write-Host ""

# 测试 3: 计算端口号
Write-Host "测试 3: 计算会话端口号" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------"
$sessionName = "test_diagnose"
$hash = 0
foreach ($char in $sessionName.ToCharArray()) {
    $hash = (($hash -shl 5) - $hash) + [int]$char
}
$port = 49152 + ([Math]::Abs($hash) % 16383)
Write-Host "  会话名: $sessionName" -ForegroundColor Cyan
Write-Host "  计算端口: $port" -ForegroundColor Cyan
Write-Host ""

# 测试 4: 检查端口是否被占用
Write-Host "测试 4: 检查端口 $port 是否可用" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------"
$connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($connections) {
    Write-Host "  ✗ 端口 $port 已被占用" -ForegroundColor Red
    Write-Host "    占用进程: $($connections.OwningProcess)" -ForegroundColor Red
    $process = Get-Process -Id $connections.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "    进程名: $($process.ProcessName)" -ForegroundColor Red
    }
} else {
    Write-Host "  ✓ 端口 $port 可用" -ForegroundColor Green
}
Write-Host ""

# 测试 5: 手动启动守护进程
Write-Host "测试 5: 尝试手动启动守护进程" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------"
if (Test-Path $daemonPath) {
    Write-Host "  执行命令: node `"$daemonPath`"" -ForegroundColor Cyan
    Write-Host "  环境变量:" -ForegroundColor Cyan
    Write-Host "    AGENT_BROWSER_DAEMON=1" -ForegroundColor Cyan
    Write-Host "    AGENT_BROWSER_SESSION=$sessionName" -ForegroundColor Cyan
    Write-Host ""

    $env:AGENT_BROWSER_DAEMON = "1"
    $env:AGENT_BROWSER_SESSION = $sessionName
    $env:CHROME_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"

    Write-Host "  启动守护进程（5秒超时）..." -ForegroundColor Cyan

    $job = Start-Job -ScriptBlock {
        param($daemonPath)
        node $daemonPath 2>&1
    } -ArgumentList $daemonPath

    Start-Sleep -Seconds 5

    # 检查守护进程是否在运行
    $pidFile = Join-Path $env:USERPROFILE ".agent-browser\$sessionName.pid"
    $portFile = Join-Path $env:USERPROFILE ".agent-browser\$sessionName.port"

    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile
        Write-Host "  ✓ PID 文件已创建: $pid" -ForegroundColor Green

        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "  ✓ 守护进程正在运行 (PID: $pid)" -ForegroundColor Green
            Write-Host "  ✓ 进程名: $($process.ProcessName)" -ForegroundColor Green
        } else {
            Write-Host "  ✗ 进程已退出 (PID: $pid)" -ForegroundColor Red
        }
    } else {
        Write-Host "  ✗ PID 文件未创建" -ForegroundColor Red
    }

    if (Test-Path $portFile) {
        $actualPort = Get-Content $portFile
        Write-Host "  ✓ Port 文件已创建: $actualPort" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Port 文件未创建" -ForegroundColor Red
    }

    # 获取守护进程输出
    $output = Receive-Job $job
    if ($output) {
        Write-Host ""
        Write-Host "  守护进程输出:" -ForegroundColor Cyan
        $output | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    }

    # 停止守护进程
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host ""
        Write-Host "  已停止测试守护进程" -ForegroundColor Cyan
    }

    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -ErrorAction SilentlyContinue

} else {
    Write-Host "  ✗ 跳过：daemon.js 未找到" -ForegroundColor Red
}
Write-Host ""

# 测试 6: 检查浏览器二进制文件
Write-Host "测试 6: 检查 Playwright 浏览器" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------"
$playwrightCache = Join-Path $env:LOCALAPPDATA "ms-playwright"
if (Test-Path $playwrightCache) {
    Write-Host "  ✓ Playwright 缓存目录存在: $playwrightCache" -ForegroundColor Green
    $chromiumDirs = Get-ChildItem $playwrightCache -Filter "chromium-*" -Directory
    if ($chromiumDirs) {
        Write-Host "  ✓ 找到 Chromium 浏览器:" -ForegroundColor Green
        foreach ($dir in $chromiumDirs) {
            Write-Host "    - $($dir.Name)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "  ✗ 未找到 Chromium 浏览器" -ForegroundColor Red
        Write-Host "    运行: npx playwright install chromium" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ Playwright 缓存目录不存在: $playwrightCache" -ForegroundColor Red
    Write-Host "    运行: npx playwright install chromium" -ForegroundColor Yellow
}
Write-Host ""

# 总结
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "诊断完成" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "常见问题解决方案:" -ForegroundColor Yellow
Write-Host "1. 如果 Node.js 未找到:" -ForegroundColor White
Write-Host "   - 确认已安装 Node.js: https://nodejs.org/" -ForegroundColor Gray
Write-Host "   - 确认 node.exe 在 PATH 环境变量中" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 如果 daemon.js 未找到:" -ForegroundColor White
Write-Host "   - 重新安装: npm uninstall -g agent-browser && npm install -g agent-browser" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 如果端口被占用:" -ForegroundColor White
Write-Host "   - 使用不同的会话名（会计算不同端口）" -ForegroundColor Gray
Write-Host "   - 或停止占用端口的进程" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 如果 Playwright 浏览器未安装:" -ForegroundColor White
Write-Host "   - 运行: npx playwright install chromium" -ForegroundColor Gray
Write-Host ""
Write-Host "5. 如果手动启动失败但无错误输出:" -ForegroundColor White
Write-Host "   - 可能是 Chromium 启动失败（权限、兼容性）" -ForegroundColor Gray
Write-Host "   - 尝试设置 CHROME_PATH 使用系统 Chrome" -ForegroundColor Gray
Write-Host ""
