import threading
import subprocess
import sys
import asyncio
import signal
import time
import queue
import json
import os
from pathlib import Path
import logging

try:
    import PySimpleGUI as sg
except ImportError:
    print("PySimpleGUI not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PySimpleGUI>=4.60"])
    import PySimpleGUI as sg

# Configure logging to file
log_dir = Path.home() / "mcp_client_logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "mcp_client.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Server configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8085
SERVER_CMD = [
    sys.executable, "-m", "src.server.mcp_server", 
    "--host", SERVER_HOST, 
    "--port", str(SERVER_PORT)
]

class MCPClientGUI:
    def __init__(self):
        self.server_process = None
        self.client_thread = None
        self.message_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.running = False
        
    def start_server(self):
        """Start the MCP server in a separate process"""
        try:
            logger.info("Starting MCP server...")
            self.server_process = subprocess.Popen(
                SERVER_CMD,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Give server time to start
            time.sleep(3)
            
            if self.server_process.poll() is None:
                logger.info("MCP server started successfully")
                return True
            else:
                logger.error("MCP server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the MCP server"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                logger.info("MCP server stopped")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                logger.warning("MCP server force killed")
            except Exception as e:
                logger.error(f"Error stopping server: {e}")
    
    def start_client_thread(self):
        """Start the client in a separate thread"""
        self.running = True
        self.client_thread = threading.Thread(target=self.run_client, daemon=True)
        self.client_thread.start()
    
    def run_client(self):
        """Run the async client in a thread"""
        try:
            # Import here to avoid circular imports
            from src.client.mcp_client import run_gui_client
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the client with GUI integration
            loop.run_until_complete(
                run_gui_client(self.message_queue, self.response_queue)
            )
        except Exception as e:
            logger.error(f"Client thread error: {e}")
            self.response_queue.put(f"Error: {e}")
    
    def create_window(self):
        """Create the main GUI window"""
        sg.theme("DarkBlue3")
        
        layout = [
            [sg.Text("MCP Client X - AI Assistant", font=("Arial", 16, "bold"))],
            [sg.Text("Status: "), sg.Text("Starting...", key="status", text_color="yellow")],
            [sg.HorizontalSeparator()],
            [sg.Multiline(
                "",
                key="chat_display",
                size=(80, 20),
                disabled=True,
                autoscroll=True,
                font=("Consolas", 10),
                background_color="black",
                text_color="white"
            )],
            [sg.Text("Your message:")],
            [sg.Input(
                "",
                key="user_input",
                size=(70, 1),
                focus=True,
                enable_events=True
            ), sg.Button("Send", bind_return_key=True)],
            [sg.Button("Clear Chat"), sg.Button("Exit"), sg.Text("", size=(30, 1)), 
             sg.Text("Press Enter to send", text_color="gray")]
        ]
        
        return sg.Window(
            "MCP Client X",
            layout,
            finalize=True,
            resizable=True,
            icon=None  # You can add an icon file here
        )
    
    def update_chat_display(self, window, message, sender=""):
        """Update the chat display with new message"""
        current_text = window["chat_display"].get()
        timestamp = time.strftime("%H:%M:%S")
        
        if sender:
            new_text = f"{current_text}[{timestamp}] {sender}: {message}\n"
        else:
            new_text = f"{current_text}{message}\n"
            
        window["chat_display"].update(new_text)
        # Auto-scroll to bottom
        window["chat_display"].set_vscroll_position(1.0)
    
    def run(self):
        """Main application loop"""
        # Start server
        if not self.start_server():
            sg.popup_error("Failed to start MCP server. Check logs for details.")
            return
        
        # Create window
        window = self.create_window()
        window["status"].update("Server started, initializing client...", text_color="orange")
        
        # Start client
        self.start_client_thread()
        
        # Wait for client to initialize
        time.sleep(2)
        window["status"].update("Ready", text_color="green")
        
        self.update_chat_display(window, "Welcome to MCP Client X!")
        self.update_chat_display(window, "You can ask me to help with file operations, weather queries, and more.")
        self.update_chat_display(window, "Type your message below and press Enter or click Send.")
        self.update_chat_display(window, "-" * 60)
        
        try:
            while True:
                event, values = window.read(timeout=100)
                
                if event in (sg.WIN_CLOSED, "Exit"):
                    break
                
                # Handle Enter key in input field
                if event == "user_input" and values["user_input"].endswith('\n'):
                    # Remove the newline and trigger send
                    user_message = values["user_input"].strip()
                    if user_message:
                        window["user_input"].update("")
                        self.handle_send_message(window, user_message)
                
                elif event == "Send":
                    user_message = values["user_input"].strip()
                    if user_message:
                        window["user_input"].update("")
                        self.handle_send_message(window, user_message)
                
                elif event == "Clear Chat":
                    window["chat_display"].update("")
                    self.update_chat_display(window, "Chat cleared.")
                
                # Check for responses from client
                try:
                    while True:
                        response = self.response_queue.get_nowait()
                        self.update_chat_display(window, response, "Assistant")
                except queue.Empty:
                    pass
                    
        except Exception as e:
            logger.error(f"GUI error: {e}")
            sg.popup_error(f"Application error: {e}")
        
        finally:
            self.cleanup()
            window.close()
    
    def handle_send_message(self, window, message):
        """Handle sending a message to the client"""
        self.update_chat_display(window, message, "You")
        self.message_queue.put(message)
        window["status"].update("Processing...", text_color="orange")
        
        # Reset status after a delay
        def reset_status():
            time.sleep(1)
            try:
                window["status"].update("Ready", text_color="green")
            except:
                pass
        
        threading.Thread(target=reset_status, daemon=True).start()
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        self.stop_server()
        logger.info("Application cleanup completed")

def main():
    """Main entry point"""
    try:
        app = MCPClientGUI()
        app.run()
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sg.popup_error(f"Failed to start application: {e}")

if __name__ == "__main__":
    main() 