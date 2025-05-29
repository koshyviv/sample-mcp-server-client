@echo off
echo ========================================
echo MCP Client X - Windows Build Script
echo ========================================

echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building executable...
pyinstaller --clean --noconfirm --onefile --windowed --name MCP_Client_X app_gui.py ^
    --hidden-import=uvicorn ^
    --hidden-import=click ^
    --hidden-import=starlette ^
    --hidden-import=fastapi ^
    --hidden-import=httpx ^
    --hidden-import=ollama ^
    --hidden-import=mcp ^
    --add-data "src;src" ^
    --icon=icon.ico

if %errorlevel% neq 0 (
    echo Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo Executable location: dist\MCP_Client_X.exe
echo ========================================
pause 