@echo off
title ProgramMind AI - 开发模式
cd /d "%~dp0"

rem 开发模式：开启 uvicorn 热重载，代码修改后自动重启。
rem 仅限本机调试使用，对内网团队提供服务请用 start.bat。
set RELOAD=true

if "%PORT%"=="" set PORT=8000

netstat -ano | findstr /c:":%PORT% " | findstr /i /c:"LISTENING" >nul
if %errorlevel%==0 (
    echo [错误] 端口 %PORT% 已被占用！请先关闭占用进程，或修改 .env 里的 PORT
    pause
    exit /b 1
)

if not exist venv\Scripts\python.exe (
    echo [错误] 未找到虚拟环境 venv，请先执行:
    echo   python -m venv venv
    echo   venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo 正在以开发模式启动（热重载已开启，仅限本机调试）...
venv\Scripts\python.exe main.py

pause
