#!/usr/bin/env python3
# coding=utf-8
"""
诊断 agent-browser 在 Windows 上的问题
"""

import subprocess
import sys
import os
import shutil

print("=" * 60)
print("agent-browser 诊断工具")
print("=" * 60)
print()

# 测试 1：检查 PATH 环境变量
print("测试 1: 检查 PATH 环境变量")
print("-" * 60)
path_env = os.environ.get('PATH', '')
print(f"PATH 长度: {len(path_env)} 字符")
print()
print("PATH 包含的目录（前 10 个）:")
for i, p in enumerate(path_env.split(os.pathsep)[:10], 1):
    print(f"  {i}. {p}")
print()

# 测试 2：使用 shutil.which 查找 agent-browser
print("测试 2: 使用 shutil.which 查找 agent-browser")
print("-" * 60)
agent_path = shutil.which("agent-browser")
if agent_path:
    print(f"✓ 找到: {agent_path}")
else:
    print("✗ 未找到 agent-browser")
print()

# 测试 3：查找 agent-browser.cmd（Windows npm 包装器）
print("测试 3: 查找 agent-browser.cmd")
print("-" * 60)
agent_cmd_path = shutil.which("agent-browser.cmd")
if agent_cmd_path:
    print(f"✓ 找到: {agent_cmd_path}")
else:
    print("✗ 未找到 agent-browser.cmd")
print()

# 测试 4：直接运行（不带 shell）
print("测试 4: subprocess.run(['agent-browser', '--version'])")
print("-" * 60)
try:
    result = subprocess.run(
        ["agent-browser", "--version"],
        capture_output=True,
        text=True,
        timeout=5,
        shell=False  # 不使用 shell
    )
    print(f"✓ 成功 (返回码: {result.returncode})")
    print(f"  输出: {result.stdout.strip()}")
except FileNotFoundError as e:
    print(f"✗ FileNotFoundError: {e}")
except Exception as e:
    print(f"✗ 其他错误: {e}")
print()

# 测试 5：使用 shell=True
print("测试 5: subprocess.run(['agent-browser', '--version'], shell=True)")
print("-" * 60)
try:
    result = subprocess.run(
        ["agent-browser", "--version"],
        capture_output=True,
        text=True,
        timeout=5,
        shell=True  # 使用 shell
    )
    print(f"✓ 成功 (返回码: {result.returncode})")
    print(f"  输出: {result.stdout.strip()}")
except Exception as e:
    print(f"✗ 错误: {e}")
print()

# 测试 6：直接运行 .cmd 文件
print("测试 6: subprocess.run(['agent-browser.cmd', '--version'])")
print("-" * 60)
try:
    result = subprocess.run(
        ["agent-browser.cmd", "--version"],
        capture_output=True,
        text=True,
        timeout=5,
        shell=False
    )
    print(f"✓ 成功 (返回码: {result.returncode})")
    print(f"  输出: {result.stdout.strip()}")
except FileNotFoundError as e:
    print(f"✗ FileNotFoundError: {e}")
except Exception as e:
    print(f"✗ 其他错误: {e}")
print()

# 测试 7：检查 Python 解释器位置
print("测试 7: Python 解释器信息")
print("-" * 60)
print(f"Python 可执行文件: {sys.executable}")
print(f"Python 版本: {sys.version}")
print(f"虚拟环境: {hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)}")
print()

print("=" * 60)
print("诊断完成")
print("=" * 60)
print()
print("建议:")
print("  - 如果测试 5 (shell=True) 成功，需要修改 agent_browser.py")
print("  - 如果测试 6 成功，可以使用 'agent-browser.cmd' 作为命令")
print("  - 如果都失败，检查 PATH 环境变量是否包含 npm 全局目录")
