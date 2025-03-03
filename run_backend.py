import sys
import os
from pathlib import Path

# Add the project root directory to the Python path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Run the backend
if __name__ == "__main__":
    # Import here after path is set up
    import uvicorn
    
    print(f"Starting backend server...")
    print(f"Python path includes: {root_dir}")
    print(f"Make sure you have installed all requirements using: pip install -r requirements.txt")
    
    # Run the server
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True) 