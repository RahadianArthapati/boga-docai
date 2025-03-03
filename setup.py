import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed successfully.")

def create_folders():
    """Create required folders"""
    folders = ["uploads"]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")

def install_poppler():
    """Check and provide instructions for poppler installation"""
    if sys.platform == "darwin":  # macOS
        print("\nPDF2Image requires poppler to be installed.")
        print("To install poppler on macOS:")
        print("  brew install poppler")
    elif sys.platform == "linux":
        print("\nPDF2Image requires poppler to be installed.")
        print("To install poppler on Ubuntu/Debian:")
        print("  sudo apt-get install poppler-utils")
    elif sys.platform == "win32":
        print("\nPDF2Image requires poppler to be installed.")
        print("To install poppler on Windows:")
        print("  1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/")
        print("  2. Extract and add to PATH")

def main():
    """Main function"""
    print("Setting up Boga DocAI...")
    
    # Create folders
    create_folders()
    
    # Install requirements
    install_requirements()
    
    # Check for poppler
    install_poppler()
    
    print("\nSetup complete!")
    print("\nTo run the application:")
    print("  1. Start the backend with: python run_backend.py")
    print("  2. Start the frontend with: python run_frontend.py")
    print("\nMake sure to set up your .env file with the required API keys.")

if __name__ == "__main__":
    main() 