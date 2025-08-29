#!/usr/bin/env python3
"""
StudyMate Application Launcher
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import fitz  # PyMuPDF
        import sentence_transformers
        import faiss
        import numpy
        print("✅ All dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def install_dependencies():
    """Install dependencies from requirements.txt"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    directories = [
        "/workspace/data",
        "/workspace/uploads", 
        "/workspace/models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def load_environment():
    """Load environment variables"""
    env_file = Path(".env")
    if env_file.exists():
        print("🔧 Loading environment variables from .env")
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("⚠️  python-dotenv not available, skipping .env file")
    else:
        print("ℹ️  No .env file found. Using default settings.")
        print("   Copy .env.example to .env and configure for IBM Watson integration.")

def main():
    """Main launcher function"""
    print("🚀 Starting StudyMate - AI-Powered PDF Q&A System")
    print("=" * 50)
    
    # Setup directories
    setup_directories()
    
    # Load environment
    load_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("\n📦 Installing missing dependencies...")
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please run:")
            print("   pip install -r requirements.txt")
            sys.exit(1)
    
    # Launch Streamlit app
    print("\n🌟 Launching StudyMate application...")
    print("📱 The app will open in your default browser")
    print("🔗 If it doesn't open automatically, visit: http://localhost:8501")
    print("\n" + "=" * 50)
    
    try:
        # Change to the directory containing app.py
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 StudyMate application stopped")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()