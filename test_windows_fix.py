#!/usr/bin/env python3
# coding=utf-8
"""
测试 Windows 平台 agent-browser 修复
"""

import platform
from trendradar.crawler.agent_browser import AgentBrowser

print("=" * 60)
print("Windows 平台修复验证")
print("=" * 60)
print()

# 检测平台
print(f"当前平台: {platform.system()}")
print()

# 创建 AgentBrowser 实例
browser = AgentBrowser(session_name="test_fix", headless=True)
print(f"AgentBrowser 实例: {browser}")
print(f"基础命令: {browser._base_cmd}")
print()

# 测试命令执行
print("测试 1: 执行 agent-browser --version")
print("-" * 60)
try:
    result = browser._run("--version")
    print(f"✓ 成功")
    print(f"  输出: {result.stdout.strip()}")
except Exception as e:
    print(f"✗ 失败: {e}")

print()
print("=" * 60)
print("如果看到 '✓ 成功' 和版本号，说明修复成功！")
print("=" * 60)
