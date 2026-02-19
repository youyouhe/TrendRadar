#!/usr/bin/env python3
"""检查环境变量和路径"""

import os
import platform

print("=" * 60)
print("环境变量检查")
print("=" * 60)
print()

print(f"平台: {platform.system()}")
print()

# 检查 AGENT_BROWSER_HOME
agent_home = os.environ.get("AGENT_BROWSER_HOME")
print(f"AGENT_BROWSER_HOME: {agent_home}")
if agent_home:
    print(f"  路径存在: {os.path.exists(agent_home)}")
    if os.path.exists(agent_home):
        daemon_js = os.path.join(agent_home, "dist", "daemon.js")
        print(f"  daemon.js 存在: {os.path.exists(daemon_js)}")
print()

# 检查 APPDATA
appdata = os.environ.get("APPDATA", "")
print(f"APPDATA: {appdata}")
print()

# 检查 npm 全局路径
npm_root = os.path.join(appdata, "npm", "node_modules", "agent-browser")
print(f"npm 全局路径: {npm_root}")
print(f"  路径存在: {os.path.exists(npm_root)}")
if os.path.exists(npm_root):
    daemon_js = os.path.join(npm_root, "dist", "daemon.js")
    print(f"  daemon.js 存在: {os.path.exists(daemon_js)}")
print()

# 如果没有设置，尝试设置
if not agent_home:
    if os.path.exists(npm_root):
        print(f"建议设置: AGENT_BROWSER_HOME={npm_root}")
        print()
        print("在 PowerShell 中执行:")
        print(f'$env:AGENT_BROWSER_HOME = "{npm_root}"')
    else:
        print("⚠️ npm 全局路径不存在！")
        print("agent-browser 可能没有全局安装。")
else:
    if not os.path.exists(agent_home):
        print("⚠️ AGENT_BROWSER_HOME 指向的路径不存在！")
        print(f"应该设置为: {npm_root}")
