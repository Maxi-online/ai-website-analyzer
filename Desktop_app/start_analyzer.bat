@echo off
chcp 65001 >nul
title Website Analyzer

echo ============================================================
echo Website Analyzer - Launch
echo ============================================================
echo.

REM Check whether the .exe exists
if exist "dist\WebsiteAnalyzer.exe" (
    echo Launching WebsiteAnalyzer.exe...
    start "" "dist\WebsiteAnalyzer.exe"
) else (
    echo .exe not found. Launching via Python...
    echo.
    python run_desktop_app.py
)

echo.
pause
