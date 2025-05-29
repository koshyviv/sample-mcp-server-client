#!/usr/bin/env python3
"""
Test script to verify MCP Client X functionality
"""
import subprocess
import sys
import time
import threading
import signal
import os

def test_server_start():
    """Test if the server can start"""
    print("Testing server startup...")
    
    server_cmd = [
        sys.executable, "-m", "src.server.mcp_server", 
        "--host", "127.0.0.1", 
        "--port", "8085"
    ]
    
    try:
        # Start server
        server_process = subprocess.Popen(
            server_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Give it time to start
        time.sleep(3)
        
        if server_process.poll() is None:
            print("✅ Server started successfully")
            
            # Test if server is responding
            import requests
            try:
                response = requests.get("http://127.0.0.1:8085/mcp", timeout=5)
                print(f"✅ Server responding: {response.status_code}")
            except Exception as e:
                print(f"⚠️  Server not responding to HTTP: {e}")
            
            # Stop server
            server_process.terminate()
            server_process.wait(timeout=5)
            print("✅ Server stopped cleanly")
            return True
        else:
            print("❌ Server failed to start")
            stdout, stderr = server_process.communicate()
            print(f"Output: {stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import PySimpleGUI as sg
        print("✅ PySimpleGUI imported")
    except ImportError as e:
        print(f"❌ PySimpleGUI import failed: {e}")
        return False
    
    try:
        from src.server import mcp_server
        print("✅ MCP Server module imported")
    except ImportError as e:
        print(f"❌ MCP Server import failed: {e}")
        return False
    
    try:
        from src.client import mcp_client
        print("✅ MCP Client module imported")
    except ImportError as e:
        print(f"❌ MCP Client import failed: {e}")
        return False
    
    return True

def test_pyinstaller():
    """Test if PyInstaller can analyze the app"""
    print("Testing PyInstaller dry run...")
    
    try:
        result = subprocess.run([
            "pyinstaller", "--clean", "--noconfirm", "--onefile", 
            "--dry-run", "app_gui.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ PyInstaller dry run successful")
            return True
        else:
            print(f"❌ PyInstaller dry run failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ PyInstaller dry run timed out")
        return False
    except Exception as e:
        print(f"❌ PyInstaller test error: {e}")
        return False

def main():
    print("=" * 50)
    print("MCP Client X - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Server Start Test", test_server_start),
        ("PyInstaller Test", test_pyinstaller),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Ready to build executable!")
        print("Run: pyinstaller --clean --noconfirm --onefile --windowed --name MCP_Client_X app_gui.py")
    else:
        print("\n🔧 Fix the failing tests before building executable")

if __name__ == "__main__":
    main() 