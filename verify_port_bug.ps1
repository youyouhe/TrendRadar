# Verify port calculation mismatch bug

Write-Host "============================================================"
Write-Host "Verify Port Calculation Mismatch"
Write-Host "============================================================"
Write-Host ""

# Test with actual session names from failed tests
$sessions = @("test_1771523393", "baidu_1771523401", "test_diagnose")

foreach ($session in $sessions) {
    Write-Host "Session: $session"
    Write-Host "------------------------------------------------------------"

    # PowerShell calculation (similar to Rust)
    $hash = 0
    foreach ($char in $session.ToCharArray()) {
        $hash = (($hash -shl 5) - $hash) + [int]$char
    }
    $portPS = 49152 + ([Math]::Abs($hash) % 16383)
    Write-Host "  PowerShell/Rust: $portPS"

    # JavaScript-style calculation (with |= 0 truncation)
    $hashJS = 0
    foreach ($char in $session.ToCharArray()) {
        $hashJS = (($hashJS -shl 5) - $hashJS) + [int]$char
        # Simulate JavaScript's |= 0 (force to 32-bit signed int)
        if ($hashJS -gt [int32]::MaxValue) {
            $hashJS = [int32]::MinValue + ($hashJS - [int32]::MaxValue - 1)
        }
        if ($hashJS -lt [int32]::MinValue) {
            $hashJS = [int32]::MaxValue + ($hashJS - [int32]::MinValue + 1)
        }
    }
    $portJS = 49152 + ([Math]::Abs($hashJS) % 16383)
    Write-Host "  JavaScript/Node: $portJS"

    if ($portPS -ne $portJS) {
        Write-Host "  [BUG] Port mismatch!" -ForegroundColor Red
    } else {
        Write-Host "  [OK] Ports match" -ForegroundColor Green
    }

    # Check if .port file exists
    $portFile = Join-Path $env:USERPROFILE ".agent-browser\$session.port"
    if (Test-Path $portFile) {
        $actualPort = Get-Content $portFile
        Write-Host "  Actual port (from file): $actualPort"

        if ($actualPort -eq $portJS) {
            Write-Host "  [CONFIRMED] Daemon uses JavaScript calculation" -ForegroundColor Green
        }
    }

    Write-Host ""
}

Write-Host "============================================================"
Write-Host "Conclusion"
Write-Host "============================================================"
Write-Host ""
Write-Host "If ports mismatch:"
Write-Host "  - This is a bug in agent-browser 0.12.0"
Write-Host "  - Rust CLI and Node.js daemon calculate different ports"
Write-Host "  - CLI tries to connect to wrong port"
Write-Host "  - Result: 'Daemon failed to start' error"
Write-Host ""
Write-Host "Workaround:"
Write-Host "  1. Report bug: https://github.com/vercel-labs/agent-browser/issues"
Write-Host "  2. Use older version: npm install -g agent-browser@0.11.0"
Write-Host "  3. Use alternative: tender-monitor-demo (Go + Rod)"
Write-Host ""
