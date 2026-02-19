#!/bin/bash
# 启动验证码识别服务

set -e

CAPTCHA_DIR="/mnt/oldroot/home/bird/tender-monitor-demo/captcha-service"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           启动验证码识别服务                               ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo

# 检查目录是否存在
if [ ! -d "$CAPTCHA_DIR" ]; then
    echo "❌ 错误：找不到验证码服务目录"
    echo "   期望位置: $CAPTCHA_DIR"
    exit 1
fi

cd "$CAPTCHA_DIR"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate

    echo "📦 安装依赖..."
    pip install -q -r requirements.txt
    echo "✓ 依赖安装完成"
else
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
fi

# 检查端口占用
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 5000 已被占用"
    read -p "是否终止现有进程? [y/N]: " kill_process
    if [ "$kill_process" = "y" ] || [ "$kill_process" = "Y" ]; then
        lsof -ti:5000 | xargs kill -9 2>/dev/null || true
        echo "✓ 已终止现有进程"
        sleep 1
    else
        echo "❌ 无法启动，端口冲突"
        exit 1
    fi
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 启动服务..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "服务地址: http://localhost:5000"
echo "健康检查: curl http://localhost:5000/health"
echo
echo "按 Ctrl+C 停止服务"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

uvicorn app:app --host 0.0.0.0 --port 5000
