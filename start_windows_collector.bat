@echo off
REM Windows 招标采集客户端启动脚本
REM 双击运行此文件即可启动采集

SETLOCAL

REM ========================================
REM 配置区域 - 根据实际情况修改
REM ========================================

REM TrendRadar服务端地址（Linux服务器）
SET SERVER_URL=http://192.168.1.100:8080

REM 客户端标识（可修改为您的机器名）
SET CLIENT_ID=windows_client

REM 是否定时运行（单位：分钟，留空则只运行一次）
REM 例如: SET SCHEDULE=30  表示每30分钟运行一次
SET SCHEDULE=

REM ========================================

echo ========================================
echo Windows 招标采集客户端
echo ========================================
echo.
echo 服务端地址: %SERVER_URL%
echo 客户端标识: %CLIENT_ID%
echo.

REM 检查Python是否安装
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 错误: 未检测到Python
    echo 请先安装Python 3.8+: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 正在检查依赖...
python -c "import requests; import yaml" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo 检测到缺少依赖，正在安装...
    pip install requests pyyaml python-dotenv
)

echo.
echo ========================================
echo 开始采集...
echo ========================================
echo.

REM 构建命令
SET CMD=python windows_tender_collector.py --server %SERVER_URL% --client-id %CLIENT_ID%

IF DEFINED SCHEDULE (
    SET CMD=%CMD% --schedule %SCHEDULE%
    echo 定时模式: 每 %SCHEDULE% 分钟采集一次
    echo 按 Ctrl+C 可以停止
) ELSE (
    echo 单次模式: 运行一次后退出
)

echo.

REM 运行采集器
%CMD%

echo.
echo ========================================
echo 程序已结束
echo ========================================
pause
