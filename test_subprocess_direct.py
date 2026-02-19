#!/usr/bin/env python3
"""直接测试 subprocess 调用 agent-browser"""

import subprocess
import time
import os
import platform

# Windows: 设置 AGENT_BROWSER_HOME 环境变量
if platform.system() == "Windows":
    if "AGENT_BROWSER_HOME" not in os.environ:
        npm_root = os.path.join(
            os.environ.get("APPDATA", ""),
            "npm", "node_modules", "agent-browser"
        )
        if os.path.exists(npm_root):
            os.environ["AGENT_BROWSER_HOME"] = npm_root
            print(f"已设置 AGENT_BROWSER_HOME: {npm_root}")
            print()

# 使用唯一会话名避免冲突
session = f"test_{int(time.time())}"

print("=" * 60)
print("直接 subprocess 测试")
print("=" * 60)
print()
print(f"会话名: {session}")
print()

# 测试1: 最简单的调用
print("测试1: 最简单的 open 命令")
cmd = ["agent-browser.cmd", "--session", session, "open", "https://example.com"]
print(f"命令: {' '.join(cmd)}")
print()

start = time.time()
result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace',
    timeout=30
)
elapsed = time.time() - start

print(f"返回码: {result.returncode}")
print(f"耗时: {elapsed:.2f} 秒")
print(f"输出: {result.stdout[:200] if result.stdout else 'None'}")
print(f"错误: {result.stderr[:200] if result.stderr else 'None'}")
print()

# 测试2: snapshot 命令
print("测试2: snapshot 命令")
cmd2 = ["agent-browser.cmd", "--session", session, "snapshot"]
print(f"命令: {' '.join(cmd2)}")
print()

start = time.time()
result2 = subprocess.run(
    cmd2,
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace',
    timeout=30
)
elapsed = time.time() - start

print(f"返回码: {result2.returncode}")
print(f"耗时: {elapsed:.2f} 秒")
print(f"输出长度: {len(result2.stdout) if result2.stdout else 0} 字符")
print()

if result.returncode == 0 and result2.returncode == 0:
    print("✅ 两个命令都成功执行！")
else:
    print("❌ 有命令执行失败")
