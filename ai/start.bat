@echo off
title ProgramMind AI - 服务启动
cd /d "%~dp0"

rem ================= 端口配置 =================
rem 修改端口：改下面这行的 8000，同时改 .env 里的 PORT
if "%PORT%"=="" set PORT=8000

rem ================= 端口占用检查 =================
netstat -ano | findstr /c:":%PORT% " | findstr /i /c:"LISTENING" >nul
if %errorlevel%==0 (
    echo.
    echo [错误] 端口 %PORT% 已被占用！
    echo   1. 查看占用进程: netstat -ano ^| findstr ":%PORT%"
    echo   2. 结束进程:     taskkill /F /PID 进程号
    echo   3. 或者修改本文件顶部的 set PORT 和 .env 里的 PORT 换端口后重试
    echo.
    pause
    exit /b 1
)

rem ================= 虚拟环境检查 =================
if not exist venv\Scripts\python.exe (
    echo [错误] 未找到虚拟环境 venv，请先执行:
    echo   python -m venv venv
    echo   venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ==============================================
echo  ProgramMind AI 服务启动中 (uvicorn 生产模式)
echo  监听地址: 0.0.0.0:%PORT%   局域网其他电脑可访问
echo  访问地址: http://本机IP:%PORT%
echo  查看本机IP: 新开命令行窗口执行 ipconfig
echo  按 Ctrl+C 停止服务
echo ==============================================
echo.

venv\Scripts\python.exe main.py

pause
