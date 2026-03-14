@echo off
title RUMI — Uninstaller

echo ============================================
echo   RUMI Uninstaller
echo ============================================
echo.
echo This will remove all RUMI Python dependencies
echo and uninstall Ollama from your system.
echo.
set /p CONFIRM=Are you sure? (yes/no): 
if /i not "%CONFIRM%"=="yes" (
    echo Cancelled.
    pause
    exit /b 0
)

:: ─── Remove Python dependencies ─────────────────────────────
echo.
echo [1/3] Removing Python packages...
pip uninstall -y ^
    openai ^
    rich ^
    PyQt6 ^
    PyQt6-WebEngine ^
    PyQt6-Qt6 ^
    PyQt6-sip ^
    PyQt6-WebEngine-Qt6 ^
    SpeechRecognition ^
    pyttsx3 ^
    PyAudio ^
    psutil ^
    requests ^
    beautifulsoup4 ^
    duckduckgo-search ^
    schedule

echo [1/3] Python packages removed.

:: ─── Remove Ollama models ────────────────────────────────────
echo.
echo [2/3] Removing Ollama models...
where ollama >nul 2>&1
if errorlevel 1 (
    echo Ollama not found in PATH, skipping model cleanup.
) else (
    for /f "tokens=1" %%m in ('ollama list ^| findstr /v "NAME"') do (
        echo Removing model: %%m
        ollama rm %%m
    )
    echo [2/3] Ollama models removed.
)

:: ─── Uninstall Ollama application ───────────────────────────
echo.
echo [3/3] Uninstalling Ollama...
set OLLAMA_UNINSTALLER=%LOCALAPPDATA%\Programs\Ollama\unins000.exe
if exist "%OLLAMA_UNINSTALLER%" (
    echo Running Ollama uninstaller...
    "%OLLAMA_UNINSTALLER%" /SILENT
    echo [3/3] Ollama uninstalled.
) else (
    echo Ollama uninstaller not found at:
    echo   %OLLAMA_UNINSTALLER%
    echo Please uninstall Ollama manually via:
    echo   Settings ^> Apps ^> Ollama ^> Uninstall
)

:: ─── Clean up Ollama data folder ────────────────────────────
echo.
echo Cleaning up Ollama data...
if exist "%LOCALAPPDATA%\Ollama" (
    rmdir /s /q "%LOCALAPPDATA%\Ollama"
    echo Removed: %LOCALAPPDATA%\Ollama
)
if exist "%USERPROFILE%\.ollama" (
    rmdir /s /q "%USERPROFILE%\.ollama"
    echo Removed: %USERPROFILE%\.ollama
)

:: ─── Clean up RUMI memory database ──────────────────────────
echo.
set /p CLEANMEM=Also delete RUMI memory/chat history (~/.rumi)? (yes/no): 
if /i "%CLEANMEM%"=="yes" (
    if exist "%USERPROFILE%\.rumi" (
        rmdir /s /q "%USERPROFILE%\.rumi"
        echo Removed: %USERPROFILE%\.rumi
    )
)

echo.
echo ============================================
echo   Uninstall complete.
echo ============================================
pause
