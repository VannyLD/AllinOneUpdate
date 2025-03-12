@echo off
set URL="https://drive.google.com/uc?export=download&id=1QNx3RTnkuDn0D22zgGVM5yiGdOQLq8sl"
set OUTPUT="downloaded_file.ext"

:: Step 1: Fetch Google Drive's confirmation token
for /f "tokens=*" %%i in ('curl -c cookie.txt -s %URL% ^| findstr "confirm"') do set TOKEN=%%i
set TOKEN=%TOKEN:confirm=%
set TOKEN=%TOKEN:amp;=%

:: Step 2: Download the full file using the extracted token
curl -Lb cookie.txt "%URL%&confirm=%TOKEN%" -o %OUTPUT%

echo Download complete!
pause
