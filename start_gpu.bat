@echo off
rem ============================================================
rem  ProgramMind AI core launcher  (start_gpu.bat)
rem
rem  Runs the formal AI core with a CUDA-enabled interpreter so
rem  Qwen2.5-7B-Instruct can use the RTX 4060 (4bit NF4).
rem
rem  - interpreter : D:\360Downloads\anaconda\envs\programmind\python.exe
rem  - workdir     : this script's folder (the project root)
rem  - sets EMBEDDING_DEVICE=cpu so bge-m3 keeps the GPU free
rem  - does NOT touch start.bat / .env / requirements.txt
rem  - never kills any process
rem ============================================================

setlocal
title ProgramMind AI Core (GPU)
cd /d "%~dp0"

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "PY_EXE=D:\360Downloads\anaconda\envs\programmind\python.exe"

if not exist "%PY_EXE%" (
    echo [ERROR] Python interpreter not found:
    echo         %PY_EXE%
    echo         Please check that the conda env "programmind" exists.
    echo.
    pause
    exit /b 1
)

if not exist "%ROOT%\main.py" (
    echo [ERROR] main.py not found: %ROOT%\main.py
    echo.
    pause
    exit /b 1
)

rem ---- keep bge-m3 on CPU, leave the GPU to Qwen 4bit ----
set "EMBEDDING_DEVICE=cpu"

if "%PORT%"=="" set "PORT=8000"

netstat -ano | findstr /i /c:"LISTENING" | findstr /c:":%PORT% " >nul 2>&1
if not errorlevel 1 (
    echo.
    echo [WARNING] Port %PORT% is already in use - not starting a second AI core.
    echo            Check with: netstat -ano ^| findstr ":%PORT%"
    echo.
    pause
    exit /b 1
)

echo ==============================================
echo  ProgramMind AI core (GPU mode)
echo   interpreter      : %PY_EXE%
echo   Qwen             : CUDA 4bit NF4
echo   EMBEDDING_DEVICE : %EMBEDDING_DEVICE%
echo   listen           : 0.0.0.0:%PORT%
echo   stop             : press Ctrl+C
echo   log              : logs\programmind.log
echo ==============================================
echo.

"%PY_EXE%" "%ROOT%\main.py"

echo.
echo [INFO] AI core exited.
pause
