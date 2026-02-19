#!/usr/bin/env python3
"""测试不捕获输出"""

import subprocess
import time

session = f"test_{int(time.time())}"

print("=" * 60)
print("测试 subprocess 不捕获输出")
print("=" * 60)
print()
print(f"会话名: {session}")
print()

# 测试1: 不捕获输出
print("测试1: 不捕获输出，直接显示到终端")
cmd = ["agent-browser.cmd", "--session", session, "open", "https://example.com"]
print(f"命令: {' '.join(cmd)}")
print()

start = time.time()
try:
    result = subprocess.run(
        cmd,
        capture_output=False,  # 不捕获输出
        timeout=10
    )
    elapsed = time.time() - start
    print()
    print(f"✓ 命令完成")
    print(f"  返回码: {result.returncode}")
    print(f"  耗时: {elapsed:.2f} 秒")
except subprocess.TimeoutExpired:
    elapsed = time.time() - start
    print()
    print(f"✗ 超时 ({elapsed:.2f} 秒)")
except KeyboardInterrupt:
    print()
    print("用户中断")

print()
print("如果这个测试快速完成，说明问题在 capture_output=True")
print("如果这个测试也卡住，说明是其他问题")
