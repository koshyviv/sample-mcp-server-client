# MCP Client X - Windows Installation Guide

## 🚀 Quick Start

### Option 1: Use the Installer (Recommended)
1. Download `MCP_Client_X_Setup.exe` from the releases page
2. Double-click to run the installer
3. Follow the installation wizard
4. Launch "MCP Client X" from your Start Menu or Desktop

### Option 2: Standalone Executable
1. Download `MCP_Client_X.exe` 
2. Double-click to run directly (no installation required)

## 📋 Prerequisites

### Required: Ollama
MCP Client X requires Ollama to be installed and running:

1. **Download Ollama for Windows**: https://ollama.ai/download/windows
2. **Install Ollama** by running the downloaded installer
3. **Pull the required model**:
   ```cmd
   ollama pull qwen3:8b
   ```
4. **Start Ollama** (it usually starts automatically after installation)

### Optional: Custom Models
You can use different models by modifying the source code. Currently supported:
- `qwen3:8b` (default)
- `llama2`
- `mistral`
- Any Ollama-compatible model

## 🎯 Features

- **File Operations**: List, create, search files and directories
- **Weather Queries**: Get current weather for any location
- **AI Chat**: Powered by Ollama with tool integration
- **Modern GUI**: Clean, dark-themed interface
- **Portable**: Single executable, no complex setup

## 💬 Usage

1. **Launch the application**
2. **Wait for initialization** (status will show "Ready")
3. **Type your message** in the input field
4. **Press Enter or click Send**

### Example Queries:
- "List files in C:\Users\YourName\Documents"
- "What's the weather in New York?"
- "Create a text file called notes.txt with some content"
- "Search for files containing 'project' in my Downloads folder"

## 🔧 Troubleshooting

### Application Won't Start
- **Check Ollama**: Make sure Ollama is running (`ollama list` in cmd)
- **Check Model**: Ensure `qwen3:8b` is installed (`ollama pull qwen3:8b`)
- **Check Logs**: Look in `%USERPROFILE%\mcp_client_logs\mcp_client.log`

### "Failed to connect to server"
- The internal MCP server failed to start
- Check Windows Firewall settings
- Try running as Administrator

### Slow Responses
- Ollama model loading can take time on first use
- Consider using a smaller model like `qwen3:1.5b`

### GUI Issues
- Try running in compatibility mode (Windows 8/10)
- Update your graphics drivers

## 📁 File Locations

- **Application**: `C:\Program Files\MCP Client X\` (if installed)
- **Logs**: `%USERPROFILE%\mcp_client_logs\`
- **Config**: Application directory

## 🔄 Updates

Check the GitHub releases page for new versions:
https://github.com/your-repo/mcp-client-x/releases

## 🆘 Support

- **Issues**: https://github.com/your-repo/mcp-client-x/issues
- **Discussions**: https://github.com/your-repo/mcp-client-x/discussions

## 🏗️ Building from Source

If you want to build the executable yourself:

1. **Install Python 3.10+**
2. **Clone the repository**
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Run build script**: `build_windows.bat`
5. **Find executable**: `dist\MCP_Client_X.exe`

## 📄 License

MIT License - see LICENSE.txt for details 