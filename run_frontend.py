import sys
import os
from pathlib import Path

# Add the project root directory to the Python path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Run the frontend
if __name__ == "__main__":
    # Import here after path is set up
    import streamlit.web.cli as stcli
    
    print(f"Starting frontend server...")
    print(f"Python path includes: {root_dir}")
    print(f"Make sure you have installed all requirements using: pip install -r requirements.txt")
    
    # Run the Streamlit app
    sys.argv = ["streamlit", "run", str(root_dir / "frontend" / "app.py")]
    sys.exit(stcli.main()) 