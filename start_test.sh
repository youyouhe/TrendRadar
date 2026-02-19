#!/bin/bash
# 招标监控系统 - 手动测试启动脚本

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║       TrendRadar 招标监控 - 手动测试启动                  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo

# 检查当前目录
if [ ! -f "test_tender_shandong.py" ]; then
    echo "❌ 错误：请在 /mnt/oldroot/home/bird/TrendRadar 目录下运行此脚本"
    exit 1
fi

# 步骤1：检查验证码服务
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 1/3: 检查验证码服务"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

CAPTCHA_SERVICE="http://localhost:5000"
if curl -s "$CAPTCHA_SERVICE/health" > /dev/null 2>&1; then
    echo "✓ 验证码服务已启动 ($CAPTCHA_SERVICE)"
else
    echo "⚠️  验证码服务未启动"
    echo
    echo "请在另一个终端运行："
    echo "  cd /mnt/oldroot/home/bird/tender-monitor-demo/captcha-service"
    echo "  source venv/bin/activate  # 如果已创建虚拟环境"
    echo "  uvicorn app:app --host 0.0.0.0 --port 5000"
    echo
    read -p "验证码服务启动后按回车继续，或按 Ctrl+C 取消..."
fi

# 步骤2：检查依赖
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 2/3: 检查依赖"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查 agent-browser
if command -v agent-browser &> /dev/null; then
    AGENT_VERSION=$(agent-browser --version 2>&1 | head -1)
    echo "✓ agent-browser: $AGENT_VERSION"
else
    echo "❌ agent-browser 未安装"
    echo "   安装命令: npm install -g agent-browser"
    exit 1
fi

# 检查 Python 依赖
echo "✓ Python 依赖检查..."
python3 -c "import requests; import pytz; print('  - requests, pytz')" 2>/dev/null || {
    echo "❌ 缺少 Python 依赖"
    echo "   安装命令: pip install -r requirements.txt"
    exit 1
}

echo "✓ 所有依赖已就绪"

# 步骤3：选择测试模式
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "步骤 3/3: 选择测试模式"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "1) 基础功能测试（快速，无需网络）"
echo "2) 山东省招标采集测试（完整，需要网络和验证码服务）"
echo "3) 退出"
echo

read -p "请选择 [1-3]: " choice

case $choice in
    1)
        echo
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "运行基础功能测试"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        python3 test_basic.py
        ;;
    2)
        echo
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "运行山东省招标采集测试"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo
        echo "测试参数："
        echo "  - 关键词: 软件开发, 系统集成"
        echo "  - 类别: 服务类"
        echo "  - 最大结果: 10 条"
        echo
        python3 test_tender_shandong.py
        ;;
    3)
        echo "退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "测试完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
