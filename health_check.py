#!/usr/bin/env python3
"""
App Health Check - Verify StudyMate Pro is running correctly
"""

import requests
import time
import subprocess
import sys
import os

def check_app_running():
    """Check if the app is running on localhost:8501"""
    print("🌐 Checking if StudyMate Pro is running...")
    
    try:
        # Try to connect to the Streamlit app
        response = requests.get("http://localhost:8501", timeout=10)
        if response.status_code == 200:
            print("✅ StudyMate Pro is running successfully!")
            print("🎉 Application accessible at: http://localhost:8501")
            return True
        else:
            print(f"❌ App responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to localhost:8501")
        print("💡 The app might still be starting up...")
        return False
    except Exception as e:
        print(f"❌ Error checking app: {e}")
        return False

def start_app_if_needed():
    """Start the app if it's not running"""
    print("\n🚀 Attempting to start StudyMate Pro...")
    
    try:
        # Use the proper Python environment
        cmd = [
            "C:/hackthon/.venv/Scripts/python.exe", 
            "-m", "streamlit", "run", "app_multi_ai.py", 
            "--server.port", "8501",
            "--server.headless", "true"
        ]
        
        print(f"📝 Command: {' '.join(cmd)}")
        
        # Start the process in the background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        print(f"⏳ Starting process (PID: {process.pid})...")
        
        # Wait a bit for startup
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Process started successfully!")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Process failed to start")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start app: {e}")
        return False

def main():
    """Main health check function"""
    print("🔍 StudyMate Pro - Health Check")
    print("=" * 40)
    
    # First, check if app is already running
    if check_app_running():
        print("\n🎉 StudyMate Pro is ready to use!")
        return True
    
    # If not running, try to start it
    print("\n🔧 App not running, attempting to start...")
    if start_app_if_needed():
        print("\n⏳ Waiting for app to fully start...")
        time.sleep(10)
        
        # Check again
        if check_app_running():
            print("\n🎉 StudyMate Pro started successfully!")
            return True
        else:
            print("\n❌ App started but not responding yet")
            print("💡 Try waiting a few more minutes and refresh your browser")
            return False
    else:
        print("\n❌ Failed to start StudyMate Pro")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "=" * 50)
        print("🌟 SUCCESS! Your StudyMate Pro is ready!")
        print("🌐 Access it at: http://localhost:8501")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("⚠️  Issues detected. Please check the output above.")
        print("=" * 50)
