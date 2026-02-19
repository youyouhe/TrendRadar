#!/usr/bin/env python3
# coding=utf-8
"""
agent-browser 详细诊断（启用详细日志）
"""

import subprocess
import os
import platform
from pathlib import Path

print("=" * 60)
print("agent-browser 详细诊断")
print("=" * 60)
print()

# 设置 Chrome 路径
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
os.environ['CHROME_PATH'] = chrome_path
print(f"CHROME_PATH: {chrome_path}")
print()

# 测试 1：查看 agent-browser 帮助信息
print("测试 1: agent-browser --help")
print("-" * 60)
agent_cmd = "agent-browser.cmd" if platform.system() == "Windows" else "agent-browser"
try:
    result = subprocess.run(
        [agent_cmd, "--help"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=5,
    )
    print(result.stdout[:500])  # 只显示前 500 字符
except Exception as e:
    print(f"✗ 错误: {e}")
print()

# 测试 2：尝试使用 --verbose 或 --debug（如果有）
print("测试 2: 尝试详细模式启动")
print("-" * 60)
print("测试命令: agent-browser --session verbose_test eval '1+1'")
print()

# 清理旧的 socket
socket_dir = Path.home() / ".agent-browser"
verbose_socket = socket_dir / "verbose_test.sock"
if verbose_socket.exists():
    verbose_socket.unlink()
    print(f"✓ 已删除旧 socket: {verbose_socket}")

try:
    # 尝试启动并捕获所有输出
    result = subprocess.run(
        [agent_cmd, "--session", "verbose_test", "eval", "1+1"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=30,
        env=os.environ,
    )

    print(f"返回码: {result.returncode}")
    print()
    print("标准输出:")
    print(result.stdout if result.stdout else "(无)")
    print()
    print("标准错误:")
    print(result.stderr if result.stderr else "(无)")

except subprocess.TimeoutExpired:
    print("✗ 超时（30秒）")
except Exception as e:
    print(f"✗ 异常: {e}")

print()

# 测试 3：检查 socket 文件是否被创建
print("测试 3: 检查 socket 文件")
print("-" * 60)
if socket_dir.exists():
    sockets = list(socket_dir.glob("*.sock"))
    if sockets:
        print(f"找到 {len(sockets)} 个 socket 文件:")
        for sock in sockets:
            stat = sock.stat()
            print(f"  - {sock.name}")
            print(f"    大小: {stat.st_size} bytes")
            print(f"    修改时间: {stat.st_mtime}")
    else:
        print("无 socket 文件")
else:
    print("配置目录不存在")

print()

# 测试 4：检查 Chrome 进程
print("测试 4: 检查 Chrome 进程")
print("-" * 60)
try:
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
        capture_output=True,
        text=True,
        encoding='gbk',  # tasklist 使用系统编码
        errors='replace',
        timeout=5,
    )
    if "chrome.exe" in result.stdout:
        print("✓ 发现 Chrome 进程在运行")
        # 统计进程数
        count = result.stdout.count("chrome.exe")
        print(f"  进程数: {count}")
    else:
        print("✗ 未发现 Chrome 进程")
except Exception as e:
    print(f"✗ 错误: {e}")

print()
print("=" * 60)
print("诊断完成")
print("=" * 60)
print()

print("建议：")
print("1. 如果看到 'Daemon failed to start'，可能的原因：")
print("   - agent-browser 0.12.0 在 Windows 上有兼容性问题")
print("   - 权限问题（Administrator 账户可能有限制）")
print("   - Windows 防火墙/安全软件阻止")
print()
print("2. 可以尝试：")
print("   方案 A：使用普通用户账户（不是 Administrator）")
print("   方案 B：降级 agent-browser 版本")
print("   方案 C：回到 tender-monitor-demo 的 Rod 方案")
print()
print("3. 降级命令：")
print("   npm uninstall -g agent-browser")
print("   npm install -g agent-browser@0.11.0")
