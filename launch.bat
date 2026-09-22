@echo off
title Antigravity Humanizer Studio
echo ========================================================
echo   Lancement de Antigravity Humanizer Studio...
echo   Port dedie : 8505 (pour eviter tout conflit avec Lyonflow)
echo ========================================================
echo.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
uv run --with streamlit --with requests --with python-docx --with pypdf --with fpdf2 --with pillow streamlit run app.py --server.port 8505
pause
