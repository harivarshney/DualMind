@echo off
title DualMind Desktop
color 0A
cls

echo.
echo     ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗
echo     ██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝
echo     ███████╗██╔████╔██║███████║██████╔╝   ██║   
echo     ╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   
echo     ███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   
echo     ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
echo.
echo          ███████╗████████╗██╗   ██╗██████╗ ██╗   ██╗
echo          ██╔════╝╚══██╔══╝██║   ██║██╔══██╗╚██╗ ██╔╝
echo          ███████╗   ██║   ██║   ██║██║  ██║ ╚████╔╝ 
echo          ╚════██║   ██║   ██║   ██║██║  ██║  ╚██╔╝  
echo          ███████║   ██║   ╚██████╔╝██████╔╝   ██║   
echo          ╚══════╝   ╚═╝    ╚═════╝ ╚═════╝    ╚═╝   
echo.
echo                      🤖 AI Desktop Version 🤖
echo.
echo ================================================================
echo                  Starting DualMind Desktop...
echo ================================================================
echo.

:: Start the application
python main.py

:: Handle exit
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Application encountered an error
    echo.
    pause
) else (
    echo.
    echo ✅ Application closed successfully
)

exit