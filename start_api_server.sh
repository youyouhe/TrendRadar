#!/bin/bash
# TrendRadar API 服务启动脚本
# 用于接收Windows客户端推送的招标信息

echo "=========================================="
echo "TrendRadar API 服务"
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
    echo "⚠️  未检测到虚拟环境"
    read -p "是否创建虚拟环境？(y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在创建虚拟环境..."
        python3 -m venv venv
        source venv/bin/activate
        echo "正在安装依赖..."
        pip install -r requirements.txt
    fi
fi

echo ""
echo "=========================================="
echo "启动服务..."
echo "=========================================="
echo ""

# 获取局域网IP
LOCAL_IP=$(ip addr show | grep "inet " | grep -v "127.0.0.1" | grep -v "docker" | grep -v "br-" | head -1 | awk '{print $2}' | cut -d'/' -f1)

echo "🌐 服务地址:"
echo "   监听地址: 0.0.0.0:$PORT (所有网络接口)"
echo "   本机访问: http://localhost:$PORT"
if [ ! -z "$LOCAL_IP" ]; then
    echo "   局域网访问: http://$LOCAL_IP:$PORT"
fi
echo ""
echo "📚 API文档: http://localhost:$PORT/docs"
echo "🔧 健康检查: http://localhost:$PORT/api/health"
echo ""
echo "📤 Windows客户端推送地址:"
if [ ! -z "$LOCAL_IP" ]; then
    echo "   http://$LOCAL_IP:$PORT/api/tenders/push"
else
    echo "   http://localhost:$PORT/api/tenders/push"
fi
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动uvicorn
uvicorn app:app --host 0.0.0.0 --port $PORT --reload
