#!/usr/bin/env python3
# coding=utf-8
"""
测试设置 Chrome 路径后的 agent-browser
"""

import os
import subprocess
import platform

print("=" * 60)
print("测试 Chrome 路径设置")
print("=" * 60)
print()

# 设置 Chrome 路径
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
os.environ['CHROME_PATH'] = chrome_path

print(f"设置 CHROME_PATH: {chrome_path}")
print()

# 测试 agent-browser
print("测试 1: 执行 agent-browser eval")
print("-" * 60)

agent_cmd = "agent-browser.cmd" if platform.system() == "Windows" else "agent-browser"

try:
    result = subprocess.run(
        [agent_cmd, "--session", "chrome_test", "eval", "console.log('Chrome OK')"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=30,
        env=os.environ,  # 传递包含 CHROME_PATH 的环境变量
    )

    if result.returncode == 0:
        print("✓ 成功！守护进程已启动")
        print(f"  输出: {result.stdout.strip()}")

        # 清理
        try:
            subprocess.run(
                [agent_cmd, "--session", "chrome_test", "close"],
                capture_output=True,
                timeout=5,
                env=os.environ,
            )
            print("  ✓ 已清理测试会话")
        except:
            pass
    else:
        print(f"✗ 失败 (返回码: {result.returncode})")
        print(f"  错误: {result.stderr.strip()}")

except subprocess.TimeoutExpired:
    print("✗ 超时（30秒）")
except Exception as e:
    print(f"✗ 异常: {e}")

print()
print("=" * 60)
print("如果看到 '✓ 成功'，说明设置 CHROME_PATH 有效")
print("=" * 60)
print()
print("下一步:")
print("  1. 在 PowerShell 中设置环境变量:")
print("     $env:CHROME_PATH = \"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\"")
print("  2. 重新运行测试:")
print("     python test_agent_browser_simple.py")
