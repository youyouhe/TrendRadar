#!/bin/bash
# TrendRadar Dashboard Web服务启动脚本

echo "=========================================="
echo "TrendRadar Dashboard Web服务"
echo "=========================================="
echo ""

# 检查端口是否被占用
PORT=8080
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 $PORT 已被占用"
    echo ""
    echo "正在运行的进程:"
    lsof -Pi :$PORT -sTCP:LISTEN
    echo ""
    read -p "是否停止现有进程并重启？(y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在停止现有进程..."
        kill -9 $(lsof -t -i:$PORT)
        sleep 2
    else
        echo "已取消启动"
        exit 1
    fi
fi

# 检查Python虚拟环境
if [ -d "venv" ]; then
    echo "✅ 检测到虚拟环境"
    source venv/bin/activate
else
    echo "⚠️  未检测到虚拟环境，使用系统Python"
fi

echo ""
echo "=========================================="
echo "启动服务..."
echo "=========================================="
echo ""
echo "🌐 Dashboard地址: http://localhost:$PORT"
echo "📚 API文档: http://localhost:$PORT/docs"
echo "🔧 健康检查: http://localhost:$PORT/api/health"
echo ""
echo "功能说明:"
echo "  • 📊 Dashboard总览 - 查看最新报告和统计数据"
echo "  • 📄 报告历史 - 浏览所有历史报告"
echo "  • 🏢 招标信息 - 搜索和查看招标项目"
echo "  • 📤 推送接收 - 接收Windows客户端推送的数据"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""
echo "=========================================="
echo ""

# 启动uvicorn
python3 -m uvicorn app:app --host 0.0.0.0 --port $PORT --reload
