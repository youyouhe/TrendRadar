#!/bin/bash
# 网络配置检查脚本

echo "========================================"
echo "TrendRadar 网络配置检查"
echo "========================================"
echo ""

# 获取局域网IP
LOCAL_IP=$(ip addr show | grep "inet " | grep -v "127.0.0.1" | grep -v "docker" | grep -v "br-" | head -1 | awk '{print $2}' | cut -d'/' -f1)

echo "📍 服务器网络信息:"
echo "   局域网IP: $LOCAL_IP"
echo ""

# 检查端口监听状态
PORT=8080
echo "🔍 检查端口 $PORT 监听状态:"
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✅ 端口 $PORT 已被监听"
    echo ""
    echo "   监听详情:"
    lsof -Pi :$PORT -sTCP:LISTEN | grep -v "COMMAND"
    echo ""

    # 检查是否监听所有接口
    if lsof -Pi :$PORT -sTCP:LISTEN | grep -q "0.0.0.0:$PORT"; then
        echo "   ✅ 监听所有网络接口 (0.0.0.0)"
        echo "   ✅ 可以从局域网访问"
    elif lsof -Pi :$PORT -sTCP:LISTEN | grep -q "127.0.0.1:$PORT"; then
        echo "   ⚠️  仅监听本地接口 (127.0.0.1)"
        echo "   ❌ 无法从局域网访问"
        echo ""
        echo "   请使用以下命令启动服务："
        echo "   ./start_dashboard.sh"
    fi
else
    echo "   ⚠️  端口 $PORT 未被监听"
    echo ""
    echo "   请先启动服务："
    echo "   ./start_dashboard.sh"
fi

echo ""
echo "🌐 访问地址："
echo "   本机: http://localhost:$PORT"
echo "   局域网: http://$LOCAL_IP:$PORT"
echo ""

# 检查防火墙状态
echo "🔥 防火墙检查："
if command -v ufw &> /dev/null; then
    if sudo ufw status 2>/dev/null | grep -q "Status: active"; then
        echo "   UFW防火墙: 已启用"
        if sudo ufw status 2>/dev/null | grep -q "$PORT"; then
            echo "   端口 $PORT: 已开放"
        else
            echo "   端口 $PORT: 未开放"
            echo "   运行以下命令开放端口："
            echo "   sudo ufw allow $PORT"
        fi
    else
        echo "   UFW防火墙: 未启用"
    fi
else
    echo "   未检测到UFW防火墙"
fi

echo ""
echo "========================================"
echo "测试建议："
echo "========================================"
echo ""
echo "1. 在服务器本机测试："
echo "   curl http://localhost:$PORT/api/health"
echo ""
echo "2. 在局域网其他机器测试："
echo "   curl http://$LOCAL_IP:$PORT/api/health"
echo "   或浏览器访问: http://$LOCAL_IP:$PORT"
echo ""
echo "3. Windows客户端配置："
echo "   编辑 start_windows_collector.bat"
echo "   SET SERVER_URL=http://$LOCAL_IP:$PORT"
echo ""
echo "========================================"
