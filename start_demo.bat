@echo off
rem ============================================================
rem  ProgramMind Demo launcher  (start_demo.bat)
rem
rem  1. cd to this script's folder (the project root)
rem  2. start the formal AI core through the EXISTING start_gpu.bat
rem  3. wait until http://127.0.0.1:8000 answers (max 60 seconds)
rem  4. start the Demo Flask backend on http://127.0.0.1:5000
rem     (the Demo always starts, even in degraded mode)
rem  5. open the browser at http://127.0.0.1:5000
rem
rem  This script DOES NOT kill any process and DOES NOT modify
rem  any config file (.env / .env.example / .gitignore / code).
rem  It only uses the conda interpreter for the Demo backend.
rem ============================================================

setlocal
title ProgramMind Demo Launcher
cd /d "%~dp0"

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "PY_EXE=D:\360Downloads\anaconda\envs\programmind\python.exe"
set "AI_URL=http://127.0.0.1:8000/"
set "DEMO_URL=http://127.0.0.1:5000"
set "AI_READY=0"

echo ============================================================
echo   ProgramMind Demo launcher
echo   formal AI core : http://127.0.0.1:8000
echo   Demo backend   : http://127.0.0.1:5000
echo ============================================================
echo.

rem ------------------------------------------------------------
rem  0) preflight checks
rem ------------------------------------------------------------
if not exist "%PY_EXE%" (
    echo [ERROR] Python interpreter not found:
    echo         %PY_EXE%
    echo         Please make sure the conda env "programmind" exists.
    echo.
    pause
    exit /b 1
)

if not exist "%ROOT%\backend\app.py" (
    echo [ERROR] Demo backend not found: %ROOT%\backend\app.py
    echo.
    pause
    exit /b 1
)

rem ------------------------------------------------------------
rem  1) formal AI core (port 8000) - reuse the existing start_gpu.bat
rem ------------------------------------------------------------
call :PORT_IN_USE 8000 PORT8000
if "%PORT8000%"=="1" (
    echo [INFO] Formal AI service is already running on port 8000.
    set "AI_READY=1"
) else (
    if exist "%ROOT%\start_gpu.bat" (
        echo [INFO] Starting formal AI service via start_gpu.bat ...
        start "ProgramMind AI Core (8000)" /D "%ROOT%" "%ROOT%\start_gpu.bat"
    ) else (
        echo [WARNING] start_gpu.bat not found - skipping formal AI core startup.
    )
)

rem ------------------------------------------------------------
rem  2) wait for the AI core: poll every 2s, 60s in total
rem     health check: GET /  (this project has no /health route)
rem ------------------------------------------------------------
if "%AI_READY%"=="1" goto :AI_DONE

echo [INFO] Waiting for the formal AI service ... (max 60s)
set /a WAITED=0

:WAIT_AI
call :CHECK_AI
if "%AI_READY%"=="1" goto :AI_DONE
set /a WAITED+=2
if %WAITED% GEQ 60 goto :AI_TIMEOUT
timeout /t 2 /nobreak >nul
goto :WAIT_AI

:AI_TIMEOUT
echo.
echo [WARNING] Formal AI service did not become ready within 60 seconds.
echo [WARNING] Starting Demo backend in degraded mode.
echo [WARNING] RAG calls will fall back to local knowledge / Mock output.
echo.

:AI_DONE
if "%AI_READY%"=="1" (
    echo [OK] Formal AI service is ready: %AI_URL%
) else (
    echo [INFO] Formal AI service is NOT ready - Demo runs in degraded mode.
)
echo.

rem ------------------------------------------------------------
rem  3) Demo backend (port 5000)
rem ------------------------------------------------------------
call :PORT_IN_USE 5000 PORT5000
if "%PORT5000%"=="1" (
    echo [INFO] Demo backend appears to be already running on port 5000.
    goto :OPEN_BROWSER
)

if not exist "%ROOT%\logs" mkdir "%ROOT%\logs"
echo [INFO] Starting Demo backend: %PY_EXE% backend\app.py
echo [INFO] Demo log file: %ROOT%\logs\demo.log
start "ProgramMind Demo (5000)" /D "%ROOT%" cmd /k ""%PY_EXE%" "%ROOT%\backend\app.py" 1>>"%ROOT%\logs\demo.log" 2>&1"
echo [INFO] Demo backend window started.

rem give Flask a short moment before opening the browser
timeout /t 3 /nobreak >nul

:OPEN_BROWSER
echo [INFO] Opening browser: %DEMO_URL%
start "" "%DEMO_URL%"
echo.
echo ============================================================
echo   Launcher finished.
echo     AI core : http://127.0.0.1:8000  (own window)
echo     Demo    : http://127.0.0.1:5000  (own window)
echo     accounts: teacher01/teacher01   student01/student01
echo   Press any key to close THIS launcher window only.
echo ============================================================
pause
endlocal
exit /b 0

rem ============================================================
rem  helper subroutines (reached only via CALL)
rem ============================================================

rem  :PORT_IN_USE <port> <out-var>
rem  sets <out-var> to 1 when the port is LISTENING, otherwise 0
:PORT_IN_USE
set "%~2=0"
netstat -ano | findstr /i /c:"LISTENING" | findstr /c:":%~1 " >nul 2>&1
if not errorlevel 1 set "%~2=1"
exit /b 0

rem  :CHECK_AI
rem  sets AI_READY=1 when GET http://127.0.0.1:8000/ returns HTTP 200
rem  (read-only health endpoint of the formal service, no side effects)
:CHECK_AI
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri '%AI_URL%' -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
if not errorlevel 1 set "AI_READY=1"
exit /b 0