# agent-browser daemon startup diagnostic (simplified version)
# Diagnose "Daemon failed to start" issue

Write-Host "============================================================"
Write-Host "agent-browser Daemon Startup Diagnosis"
Write-Host "============================================================"
Write-Host ""

# Test 1: Check Node.js
Write-Host "Test 1: Check Node.js"
Write-Host "------------------------------------------------------------"
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCmd) {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "  [OK] Node.js: $nodeVersion"
    Write-Host "  [OK] npm: $npmVersion"
} else {
    Write-Host "  [ERROR] Node.js not found in PATH"
    Write-Host "  This is the main reason for daemon startup failure"
    exit 1
}
Write-Host ""

# Test 2: Check daemon.js
Write-Host "Test 2: Check daemon.js file"
Write-Host "------------------------------------------------------------"
$npmPrefix = npm prefix -g
$daemonPath = Join-Path $npmPrefix "node_modules\agent-browser\dist\daemon.js"
if (Test-Path $daemonPath) {
    Write-Host "  [OK] daemon.js found: $daemonPath"
} else {
    Write-Host "  [WARN] daemon.js not found at: $daemonPath"
    Write-Host "  Checking alternative locations..."

    $altPath1 = Join-Path $npmPrefix "node_modules\agent-browser\daemon.js"
    $altPath2 = ".\dist\daemon.js"

    if (Test-Path $altPath1) {
        Write-Host "  [OK] Found at: $altPath1"
        $daemonPath = $altPath1
    } elseif (Test-Path $altPath2) {
        Write-Host "  [OK] Found at: $altPath2"
        $daemonPath = $altPath2
    } else {
        Write-Host "  [ERROR] daemon.js not found anywhere"
        Write-Host "  agent-browser may not be installed correctly"
    }
}
Write-Host ""

# Test 3: Calculate port number
Write-Host "Test 3: Calculate session port"
Write-Host "------------------------------------------------------------"
$sessionName = "test_diagnose"
$hash = 0
foreach ($char in $sessionName.ToCharArray()) {
    $hash = (($hash -shl 5) - $hash) + [int]$char
}
$port = 49152 + ([Math]::Abs($hash) % 16383)
Write-Host "  Session: $sessionName"
Write-Host "  Port: $port"
Write-Host ""

# Test 4: Check if port is available
Write-Host "Test 4: Check if port $port is available"
Write-Host "------------------------------------------------------------"
$connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($connections) {
    Write-Host "  [ERROR] Port $port is already in use"
    Write-Host "  Process ID: $($connections.OwningProcess)"
    $process = Get-Process -Id $connections.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "  Process name: $($process.ProcessName)"
    }
} else {
    Write-Host "  [OK] Port $port is available"
}
Write-Host ""

# Test 5: Try to start daemon manually
Write-Host "Test 5: Try to start daemon manually"
Write-Host "------------------------------------------------------------"
if (-not (Test-Path $daemonPath)) {
    Write-Host "  [SKIP] daemon.js not found"
} else {
    Write-Host "  Command: node `"$daemonPath`""
    Write-Host "  Environment:"
    Write-Host "    AGENT_BROWSER_DAEMON=1"
    Write-Host "    AGENT_BROWSER_SESSION=$sessionName"
    Write-Host ""

    $env:AGENT_BROWSER_DAEMON = "1"
    $env:AGENT_BROWSER_SESSION = $sessionName
    $env:CHROME_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"

    Write-Host "  Starting daemon (5 second timeout)..."

    $job = Start-Job -ScriptBlock {
        param($daemon)
        Set-Location $using:PWD
        $env:AGENT_BROWSER_DAEMON = "1"
        $env:AGENT_BROWSER_SESSION = $using:sessionName
        $env:CHROME_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
        node $daemon 2>&1
    } -ArgumentList $daemonPath

    Start-Sleep -Seconds 5

    # Check if daemon is running
    $pidFile = Join-Path $env:USERPROFILE ".agent-browser\$sessionName.pid"
    $portFile = Join-Path $env:USERPROFILE ".agent-browser\$sessionName.port"

    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile
        Write-Host "  [OK] PID file created: $pid"

        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "  [OK] Daemon is running (PID: $pid)"
            Write-Host "  [OK] Process: $($process.ProcessName)"
        } else {
            Write-Host "  [ERROR] Process exited (PID: $pid)"
        }
    } else {
        Write-Host "  [ERROR] PID file not created"
    }

    if (Test-Path $portFile) {
        $actualPort = Get-Content $portFile
        Write-Host "  [OK] Port file created: $actualPort"
    } else {
        Write-Host "  [ERROR] Port file not created"
    }

    # Get daemon output
    $output = Receive-Job $job
    if ($output) {
        Write-Host ""
        Write-Host "  Daemon output:"
        $output | ForEach-Object { Write-Host "    $_" }
    }

    # Stop daemon
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host ""
        Write-Host "  Stopped test daemon"
    }

    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -ErrorAction SilentlyContinue
}
Write-Host ""

# Test 6: Check Playwright Chromium
Write-Host "Test 6: Check Playwright Chromium"
Write-Host "------------------------------------------------------------"
$playwrightCache = Join-Path $env:LOCALAPPDATA "ms-playwright"
if (Test-Path $playwrightCache) {
    Write-Host "  [OK] Playwright cache exists: $playwrightCache"
    $chromiumDirs = Get-ChildItem $playwrightCache -Filter "chromium-*" -Directory -ErrorAction SilentlyContinue
    if ($chromiumDirs) {
        Write-Host "  [OK] Found Chromium browser:"
        foreach ($dir in $chromiumDirs) {
            Write-Host "    - $($dir.Name)"
        }
    } else {
        Write-Host "  [WARN] Chromium browser not found"
        Write-Host "  Run: npx playwright install chromium"
    }
} else {
    Write-Host "  [WARN] Playwright cache not found: $playwrightCache"
    Write-Host "  Run: npx playwright install chromium"
}
Write-Host ""

# Summary
Write-Host "============================================================"
Write-Host "Diagnosis Complete"
Write-Host "============================================================"
Write-Host ""
Write-Host "Common Solutions:"
Write-Host "1. If Node.js not found:"
Write-Host "   - Install Node.js from: https://nodejs.org/"
Write-Host "   - Ensure node.exe is in PATH"
Write-Host ""
Write-Host "2. If daemon.js not found:"
Write-Host "   - Reinstall: npm uninstall -g agent-browser"
Write-Host "              npm install -g agent-browser"
Write-Host ""
Write-Host "3. If port is in use:"
Write-Host "   - Use a different session name"
Write-Host "   - Or stop the process using the port"
Write-Host ""
Write-Host "4. If Playwright Chromium not installed:"
Write-Host "   - Run: npx playwright install chromium"
Write-Host ""
Write-Host "5. If manual start fails with no output:"
Write-Host "   - Chromium may fail to start (permissions, compatibility)"
Write-Host "   - Try setting CHROME_PATH to use system Chrome"
Write-Host ""
