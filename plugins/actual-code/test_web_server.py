#!/usr/bin/env python3
"""
Quick test to verify web server can start
"""

import requests
import time
import subprocess
import sys
from multiprocessing import Process

def start_server():
    """Start the web server"""
    import web_server
    web_server.socketio.run(web_server.app, host='0.0.0.0', port=5001)

def test_server():
    """Test if server is responding"""
    time.sleep(3)  # Wait for server to start
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:5001/api/health')
        if response.status_code == 200:
            data = response.json()
            print("✅ Web server is healthy!")
            print(f"   Status: {data['status']}")
            print(f"   GitHub configured: {data['github_token_configured']}")
            print(f"   Google Cloud configured: {data['google_cloud_configured']}")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing ActualCode Web Server...")
    print()
    
    # Start server in background
    server_process = Process(target=start_server)
    server_process.start()
    
    try:
        # Test the server
        success = test_server()
        
        if success:
            print()
            print("✅ All tests passed!")
            print("🌐 Web UI is ready at: http://localhost:5001")
            print()
            print("To start the server manually, run:")
            print("  ./start_web_ui.sh")
        else:
            print()
            print("❌ Tests failed. Check the error messages above.")
            sys.exit(1)
    finally:
        # Stop the server
        server_process.terminate()
        server_process.join(timeout=2)
        if server_process.is_alive():
            server_process.kill()
