@echo off
setlocal EnableExtensions EnableDelayedExpansion
title RUMI - One-click Setup and Launch

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

set "VENV_DIR=%PROJECT_DIR%.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "RUMI_MODEL=llama3.2:3b"
set "RUMI_REQUEST_TIMEOUT=300"
set "OLLAMA_HOME=%PROJECT_DIR%.ollama"
set "OLLAMA_MODELS=%PROJECT_DIR%.ollama\models"
set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
set "OLLAMA_INSTALLER=%PROJECT_DIR%OllamaSetup.exe"

echo ============================================================
echo   RUMI Launcher (Windows)
echo ============================================================
echo Project: %PROJECT_DIR%
echo.

:: 1) Ensure Python exists
where py >nul 2>&1
if %errorlevel% neq 0 (
    where python >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python not found. Install Python 3.10+ and run again.
        pause
        exit /b 1
    )
)

:: 2) Create local virtual environment inside project folder
if not exist "%VENV_PY%" (
    echo [1/5] Creating project-local virtual environment...
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        py -3 -m venv "%VENV_DIR%"
    ) else (
        python -m venv "%VENV_DIR%"
    )
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: 3) Install Python dependencies in local venv
echo [2/5] Installing Python dependencies in .venv...
"%VENV_PY%" -m pip install --upgrade pip >nul
"%VENV_PY%" -m pip install -r "%PROJECT_DIR%requirements.txt"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)

:: 4) Ensure Ollama is installed
if not exist "%OLLAMA_EXE%" (
    echo [3/5] Ollama not found. Downloading installer to project folder...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -UseBasicParsing -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%OLLAMA_INSTALLER%'"
    if not exist "%OLLAMA_INSTALLER%" (
        echo [ERROR] Could not download Ollama installer.
        pause
        exit /b 1
    )

    echo [3/5] Installing Ollama silently...
    start /wait "" "%OLLAMA_INSTALLER%" /S

    if not exist "%OLLAMA_EXE%" (
        echo [ERROR] Ollama install did not complete as expected.
        echo Install manually from: https://ollama.com/download/windows
        pause
        exit /b 1
    )
)

:: 5) Start Ollama if needed
echo [4/5] Checking Ollama server...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [4/5] Starting Ollama server...
    start "" "%OLLAMA_EXE%" serve

    set "TRIES=0"
    :wait_ollama
    set /a TRIES+=1
    curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
    if not errorlevel 1 goto ollama_ready
    if !TRIES! geq 30 (
        echo [ERROR] Ollama server did not respond in time.
        pause
        exit /b 1
    )
    timeout /t 1 /nobreak >nul
    goto wait_ollama
)

:ollama_ready
echo [4/5] Pulling model if needed: %RUMI_MODEL%
"%OLLAMA_EXE%" pull %RUMI_MODEL%

:: 6) Launch GUI with local environment
echo [5/5] Launching RUMI GUI...
"%VENV_PY%" "%PROJECT_DIR%gui.py"

echo.
echo RUMI closed.
pause
