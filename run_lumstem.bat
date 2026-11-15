@echo off
setlocal
title LUMSTEM - Planetary Analog Mission Control
echo ============================================================================
echo    LUMSTEM // Multi-Modal Planetary Analog Engine (NASA Space Apps 2026)
echo ============================================================================
echo.

REM --- 1. Detect mode: Quick Launch (Judges) vs Developer Rebuild (Teammates) ---
REM Pass --dev or --rebuild in terminal to force environment setup & data.js compilation
set "FORCE_BUILD=0"
if /i "%~1"=="--dev" set "FORCE_BUILD=1"
if /i "%~1"=="--rebuild" set "FORCE_BUILD=1"

if not exist "web\data.js" (
    echo [INFO] Pre-compiled web\data.js not found. Switching to Developer Build Mode...
    set "FORCE_BUILD=1"
) else (
    if "%FORCE_BUILD%"=="0" (
        echo [FAST MODE] Pre-compiled web\data.js detected!
        echo  - Judges / Viewers: Launching automatically in 2 seconds ^(zero installs required^).
        echo  - Teammates / Devs: Press [R] now if you need to set up .venv/Conda and rebuild web\data.js.
        choice /c LR /n /t 2 /d L /m "Press [R] to Rebuild data.js, or wait 2s for instant [L]aunch: "
        if errorlevel 2 set "FORCE_BUILD=1"
    )
)

REM --- 2. Locate Python executable (supports Conda, python, and Windows py launcher) ---
set "PYTHON_CMD="
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
) else (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=py"
    )
)

REM --- 3. Zero-Python Emergency Fallback for Judges ---
if "%PYTHON_CMD%"=="" (
    if exist "web\data.js" (
        echo.
        echo [FALLBACK] Python was not detected in PATH, but web\data.js is ready!
        echo Opening web\index.html directly in your default browser...
        start "" "%~dp0web\index.html"
        exit /b 0
    ) else (
        echo [ERROR] Python is not installed or not in PATH, and web\data.js is missing.
        echo Please install Python 3.9+ or Miniconda and check "Add Python to PATH".
        pause
        exit /b 1
    )
)

REM --- 4. Developer Environment Setup & Data Compilation (Runs if R pressed or data.js missing) ---
if "%FORCE_BUILD%"=="1" (
    echo.
    echo [DEV MODE] Setting up Python environment and compiling web\data.js...
    
    REM Prefer Conda if installed on teammate's laptop; otherwise create/use standard .venv
    where conda >nul 2>&1
    if %errorlevel% equ 0 (
        echo [ENV] Conda detected. Activating Conda environment...
        call conda activate lumstem >nul 2>&1 || call conda activate base >nul 2>&1
    ) else (
        if not exist ".venv\Scripts\activate.bat" (
            echo [1/3] Creating isolated Python virtual environment ^(.venv^)...
            %PYTHON_CMD% -m venv .venv
        )
        echo [ENV] Activating .venv...
        call .venv\Scripts\activate.bat
        set "PYTHON_CMD=python"
    )

    echo [2/3] Ensuring numpy and pandas are installed...
    %PYTHON_CMD% -m pip install --upgrade pip --quiet
    %PYTHON_CMD% -m pip install numpy pandas --quiet

    echo [3/3] Running build_web_data.py ^(compiling CSVs into web\data.js^)...
    %PYTHON_CMD% build_web_data.py
    if %errorlevel% neq 0 (
        echo [ERROR] build_web_data.py failed. Ensure data\tiles\metadata.csv, data\scores\vision.csv, and data\scores\scalar.csv are in place.
        pause
        exit /b 1
    )
    echo [OK] web\data.js successfully rebuilt!
)

REM --- 5. Launch Local Web Server and Open Browser ---
echo.
echo [LAUNCH] Starting LUMSTEM Mission Control at http://localhost:8080 ...
echo  - Frontend file: web\index.html ^(edit and refresh browser to see UI changes live!^)
echo  - Keep this window open while using the application.
echo  - Press Ctrl+C at any time to stop the server.
echo.

start "" "http://localhost:8080"
%PYTHON_CMD% -m http.server 8080 --directory web
pause