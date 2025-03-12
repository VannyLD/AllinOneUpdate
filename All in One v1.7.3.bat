@echo off
echo Downloading latest version...
PowerShell -Command "& {Invoke-WebRequest -Uri 'https://drive.usercontent.google.com/download?id=1QNx3RTnkuDn0D22zgGVM5yiGdOQLq8sl&export=download&authuser=0&confirm=t&uuid=510a94a4-177d-44a7-b4da-2d4924c17fb0&at=AEz70l4GcPmNAPm0oEZUton4kMv8:1741811441686' -OutFile 'All_in_One v1.7.4.exe'}"
echo Download complete!
pause
