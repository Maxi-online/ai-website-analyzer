@echo off
chcp 65001 >nul
echo ============================================================
echo Building .exe for Website Analyzer
echo ============================================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller is not installed. Installing...
    pip install pyinstaller
)

echo.
echo Building application...
echo.

REM Build a single-file GUI executable (no console)
pyinstaller --onefile ^
    --windowed ^
    --name="WebsiteAnalyzer" ^
    --add-data "settings.py;." ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.scrolledtext ^
    --hidden-import=requests ^
    --hidden-import=json ^
    --hidden-import=threading ^
    desktop_app.py

echo.
echo ============================================================
echo Done! WebsiteAnalyzer.exe has been created in the dist/ folder
echo ============================================================
echo.
pause
