@echo off
title Partage distant illimite - AI-Remover
echo ========================================================
echo   Partage distant illimite (Cloudflare Tunnel)
echo   AI-Remover
echo ========================================================
echo.
echo Port par defaut : 8505
echo.
set /p PORT="Entrez le port [Appuyez sur Entree pour 8505] : "
if "%PORT%"=="" set PORT=8505
echo.
echo Verification de Cloudflare Tunnel...

set CF_EXE=cloudflared
where cloudflared >nul 2>nul
if %errorlevel% neq 0 (
    if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" (
        set CF_EXE="C:\Program Files (x86)\cloudflared\cloudflared.exe"
    ) else if exist "C:\Program Files\cloudflared\cloudflared.exe" (
        set CF_EXE="C:\Program Files\cloudflared\cloudflared.exe"
    ) else (
        echo [!] cloudflared n'est pas installe. Tentative d'installation automatique via winget...
        winget install --id Cloudflare.cloudflared --silent --accept-package-agreements --accept-source-agreements
        if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" (
            set CF_EXE="C:\Program Files (x86)\cloudflared\cloudflared.exe"
        ) else if exist "C:\Program Files\cloudflared\cloudflared.exe" (
            set CF_EXE="C:\Program Files\cloudflared\cloudflared.exe"
        )
    )
)

echo Initialisation du tunnel Cloudflare securise pour le port %PORT%...
echo.
echo --------------------------------------------------------
echo Votre lien public illimite (https://...trycloudflare.com)
echo va apparaitre ci-dessous.
echo (Laissez cette fenetre ouverte pour maintenir le partage)
echo --------------------------------------------------------
echo.

%CF_EXE% tunnel --url http://localhost:%PORT%

pause
