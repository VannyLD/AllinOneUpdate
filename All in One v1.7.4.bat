@echo off
setlocal

echo Closing current application...
taskkill /IM "MAX PREMIUM PRO v1.0.1.exe" /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo Downloading new version...
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://github.com/VannyLD/MAXPREMIUMPRO/releases/download/v1.0.1/MAX.PREMIUM.PRO.v1.0.2.exe', 'MAX PREMIUM PRO v1.0.2.exe')"

if exist "MAX PREMIUM PRO v1.0.2.exe" (
    echo Starting new version...
    start "" "MAX PREMIUM PRO v1.0.2.exe"

    echo Cleaning up...
    del "%~f0"
) else (
    echo Failed to download the new version. Please check your internet connection or try again later.
    pause
)

endlocal
