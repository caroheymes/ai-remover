@echo off
title AI-Remover Internal API
echo ========================================================
echo   Lancement de l'API interne AI-Remover...
echo   Port dedie : 8506 (Swagger Docs : http://127.0.0.1:8506/docs)
echo ========================================================
echo.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8506 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>&1
uv run --with fastapi --with uvicorn --with requests uvicorn api:app --host 127.0.0.1 --port 8506
pause
