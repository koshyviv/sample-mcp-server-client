#!/bin/bash
echo "========================================"
echo "MCP Client X - Linux Build Script"
echo "========================================"

echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

echo ""
echo "Building executable..."
pyinstaller --clean --noconfirm --onefile --windowed --name MCP_Client_X app_gui.py \
    --hidden-import=uvicorn \
    --hidden-import=click \
    --hidden-import=starlette \
    --hidden-import=fastapi \
    --hidden-import=httpx \
    --hidden-import=ollama \
    --hidden-import=mcp \
    --add-data "src:src"

if [ $? -ne 0 ]; then
    echo "Build failed"
    exit 1
fi

echo ""
echo "========================================"
echo "Build completed successfully!"
echo "Executable location: dist/MCP_Client_X"
echo "========================================" 