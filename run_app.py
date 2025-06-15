#!/usr/bin/env python3
"""
Startup script to run both FastAPI backend and Streamlit frontend.
"""

import subprocess
import sys
import time
import signal
import os
from threading import Thread
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_fastapi():
    """Run the FastAPI backend server."""
    print("🚀 Starting FastAPI backend server...")
    try:
        subprocess.run([
            sys.executable, "main.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ FastAPI server failed: {e}")
    except KeyboardInterrupt:
        print("🛑 FastAPI server stopped")

def run_streamlit():
    """Run the Streamlit frontend."""
    print("🎨 Starting Streamlit frontend...")
    # Wait a bit for FastAPI to start
    time.sleep(3)
    
    # Get port from environment
    streamlit_port = os.getenv("STREAMLIT_PORT", "8501")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", streamlit_port,
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit server failed: {e}")
    except KeyboardInterrupt:
        print("🛑 Streamlit server stopped")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n🛑 Shutting down servers...")
    sys.exit(0)

def main():
    """Main function to run both servers."""
    print("🏥 MediBook - Starting Application Servers")
    print("=" * 50)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start FastAPI in a separate thread
    fastapi_thread = Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Start Streamlit in main thread
    try:
        run_streamlit()
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    
    print("👋 Goodbye!")

if __name__ == "__main__":
    main() 