#!/usr/bin/env python3
# coding=utf-8
"""
诊断 agent-browser 浏览器启动问题
"""

import subprocess
import os
import shutil
import platform
from pathlib import Path

print("=" * 60)
print("agent-browser 浏览器启动诊断")
print("=" * 60)
print()

# 测试 1：检查平台信息
print("测试 1: 平台信息")
print("-" * 60)
print(f"操作系统: {platform.system()}")
print(f"系统版本: {platform.version()}")
print(f"用户主目录: {Path.home()}")
print()

# 测试 2：检查浏览器
print("测试 2: 检查可用浏览器")
print("-" * 60)

browsers = {
    "Chrome": "chrome",
    "Edge": "msedge",
    "Chromium": "chromium"
}

found_browsers = []
for name, cmd in browsers.items():
    path = shutil.which(cmd)
    if path:
        print(f"✓ {name}: {path}")
        found_browsers.append(name)
    else:
        if platform.system() == "Windows":
            # 尝试常见的 Windows 路径
            common_paths = [
                f"C:\\Program Files\\Google\\Chrome\\Application\\{cmd}.exe",
                f"C:\\Program Files (x86)\\Google\\Chrome\\Application\\{cmd}.exe",
                f"C:\\Program Files\\Microsoft\\Edge\\Application\\{cmd}.exe",
                f"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\{cmd}.exe",
            ]
            for p in common_paths:
                if Path(p).exists():
                    print(f"✓ {name}: {p} (不在 PATH 中)")
                    found_browsers.append(name)
                    break
            else:
                print(f"✗ {name}: 未找到")
        else:
            print(f"✗ {name}: 未找到")

if not found_browsers:
    print()
    print("⚠️  警告：未找到任何浏览器！")
    print("   agent-browser 需要 Chrome、Edge 或 Chromium")
else:
    print()
    print(f"✓ 找到浏览器: {', '.join(found_browsers)}")

print()

# 测试 3：检查 agent-browser socket 目录
print("测试 3: 检查 agent-browser 配置目录")
print("-" * 60)
agent_dir = Path.home() / ".agent-browser"
print(f"配置目录: {agent_dir}")
if agent_dir.exists():
    print(f"  ✓ 目录存在")
    # 列出 socket 文件
    sockets = list(agent_dir.glob("*.sock"))
    if sockets:
        print(f"  ⚠️  发现 {len(sockets)} 个残留 socket 文件:")
        for sock in sockets[:5]:  # 只显示前 5 个
            print(f"    - {sock.name}")
        if len(sockets) > 5:
            print(f"    ... 还有 {len(sockets) - 5} 个")
    else:
        print(f"  ✓ 无残留 socket 文件")
else:
    print(f"  ✓ 目录不存在（首次运行）")
print()

# 测试 4：测试 agent-browser 命令执行
print("测试 4: 测试 agent-browser 命令")
print("-" * 60)
agent_cmd = "agent-browser.cmd" if platform.system() == "Windows" else "agent-browser"
try:
    result = subprocess.run(
        [agent_cmd, "--version"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=5,
    )
    print(f"✓ 命令执行成功")
    print(f"  版本: {result.stdout.strip()}")
except Exception as e:
    print(f"✗ 命令执行失败: {e}")
print()

# 测试 5：尝试清理并手动启动
print("测试 5: 尝试手动启动（简单测试）")
print("-" * 60)
print("清理残留 socket 文件...")
if agent_dir.exists():
    try:
        for sock in agent_dir.glob("*.sock"):
            sock.unlink()
        print("  ✓ 已清理残留文件")
    except Exception as e:
        print(f"  ✗ 清理失败: {e}")
else:
    print("  ✓ 无需清理")

print()
print("尝试执行简单命令（eval 'console.log(\"test\")'）...")
try:
    test_session = "diagnose_test"
    result = subprocess.run(
        [agent_cmd, "--session", test_session, "eval", "console.log('test')"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=30,  # 首次启动可能需要更长时间
    )
    if result.returncode == 0:
        print(f"✓ 浏览器守护进程启动成功")
        print(f"  输出: {result.stdout.strip()}")

        # 清理测试会话
        try:
            subprocess.run(
                [agent_cmd, "--session", test_session, "close"],
                capture_output=True,
                timeout=5,
            )
        except:
            pass
    else:
        print(f"✗ 启动失败 (返回码: {result.returncode})")
        print(f"  错误信息: {result.stderr.strip()}")
except subprocess.TimeoutExpired:
    print(f"✗ 超时（30秒）")
except Exception as e:
    print(f"✗ 异常: {e}")

print()
print("=" * 60)
print("诊断完成")
print("=" * 60)
print()

# 建议
print("建议:")
if not found_browsers:
    print("  1. ⚠️  安装浏览器（Chrome 或 Edge）")
    print("     - Chrome: https://www.google.com/chrome/")
    print("     - Edge: https://www.microsoft.com/edge")
elif agent_dir.exists() and list(agent_dir.glob("*.sock")):
    print("  1. 清理残留 socket 文件:")
    print(f"     Remove-Item -Recurse -Force \"{agent_dir}\"")
    print("  2. 重新运行测试")
else:
    print("  1. 尝试手动运行 agent-browser:")
    print(f"     {agent_cmd} open https://www.baidu.com")
    print("  2. 检查是否有防火墙/安全软件阻止")
    print("  3. 查看上述测试 5 的详细错误信息")
