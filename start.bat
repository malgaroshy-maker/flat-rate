@echo off
setlocal enabledelayedexpansion
set ROOT=%~dp0

echo ========================================
echo   Smart Labor Cost Estimator v1
echo ========================================
echo.

rem --- Python check ---
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.12+
    pause & exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo [ OK ] Python %%v

rem --- Node check ---
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Install Node 22+
    pause & exit /b 1
)
for /f "tokens=1,2 delims=v" %%v in ('node --version 2^>^&1') do echo [ OK ] Node %%w

echo.

rem --- Venv check ---
if not exist "%ROOT%backend\venv\Scripts\python.exe" (
    echo WARNING: Python venv not found, creating...
    cd /d "%ROOT%backend"
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Python deps
        pause & exit /b 1
    )
    echo [ OK ] Venv created
) else (
    echo [ OK ] Python venv
)

rem --- Node modules check ---
if not exist "%ROOT%frontend\node_modules" (
    echo WARNING: node_modules not found, installing...
    cd /d "%ROOT%frontend"
    call npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Node deps
        pause & exit /b 1
    )
    echo [ OK ] npm install complete
) else (
    echo [ OK ] Node modules
)

rem --- .env check ---
if not exist "%ROOT%backend\.env" (
    if exist "%ROOT%backend\.env.template" (
        echo Creating .env from template...
        copy "%ROOT%backend\.env.template" "%ROOT%backend\.env" >nul
        echo WARNING: Fill in your GEMINI_API_KEY in backend\.env
    ) else (
        echo WARNING: No .env or .env.template found
    )
) else (
    echo [ OK ] .env file
)

rem --- Gemini API key check ---
cd /d "%ROOT%backend"
for /f "tokens=2 delims==" %%a in ('findstr /b "GEMINI_API_KEY=" .env 2^>nul') do set KEY=%%a
if "!KEY!"=="" (
    echo [ !! ] Gemini API key NOT set - cloud features disabled
) else if "!KEY!"=="your-api-key-here" (
    echo [ !! ] Gemini API key shows default value - cloud features disabled
) else (
    echo [ OK ] Gemini API key
)

rem --- ChromaDB check ---
cd /d "%ROOT%backend"
call venv\Scripts\python.exe -c "from vector_store import get_or_create_collection; c=get_or_create_collection(); print(c.count())" >nul 2>nul
if %errorlevel% neq 0 (
    echo [ !! ] ChromaDB appears empty - run scripts\ingest.py first
) else (
    echo [ OK ] ChromaDB
)

echo.
echo ========================================
echo [ 1/2 ] Starting backend on :8000 ...
echo ========================================
start "Labor Backend" cmd /c "cd /d %ROOT%backend && %ROOT%backend\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo Waiting for backend to be ready...
set RETRY=0
:health_loop
set /a RETRY+=1
curl -s http://127.0.0.1:8000/api/health >nul 2>nul
if %errorlevel% equ 0 goto backend_ready
ping 127.0.0.1 -n 2 >nul 2>nul
if !RETRY! lss 15 goto health_loop
echo ERROR: Backend failed to start in 30 seconds
echo Check %ROOT%backend\.env and try again
pause & exit /b 1

:backend_ready
echo [ OK ] Backend ready ^(!RETRY! retries^)

echo.
echo ========================================
echo [ 2/2 ] Starting frontend on :3000 ...
echo ========================================
start "Labor Frontend" cmd /c "cd /d %ROOT%frontend && npx next dev --port 3000"

echo.
echo ========================================
echo   All systems running
echo ========================================
echo   Frontend : http://localhost:3000
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo   Health   : http://localhost:8000/api/health
echo ========================================
echo.
echo Close this window to stop all servers.
pause
