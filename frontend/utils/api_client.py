import os
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class APIClient:
    """Client for backend API"""
    
    def __init__(self):
        """Initialize API client"""
        self.base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.api_url = f"{self.base_url}/api/v1"
        self.documents_url = f"{self.api_url}/documents"
    
    def upload_file(self, file) -> Dict[str, Any]:
        """Upload a file to the backend"""
        try:
            # Create file payload
            files = {"file": file}
            
            # Send request
            response = requests.post(
                f"{self.documents_url}/upload",
                files=files
            )
            
            # Check response
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to upload file")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_file(self, file_id: str, file_type: str) -> Dict[str, Any]:
        """Process a file with OCR and LLM"""
        try:
            # In our updated API, the upload endpoint already processes the file
            # So we'll just return what we have or attempt to get the file info
            return {
                "success": True,
                "result": {
                    "file_id": file_id,
                    "file_type": file_type,
                    "message": "File processed during upload"
                }
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_text(self, text: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """Process raw text with LLM"""
        try:
            # This endpoint no longer exists, but we can simulate it
            # by creating a temporary file and uploading it
            # For now, we'll just return a message
            return {
                "success": True,
                "result": {
                    "message": "Text processing is not available in the current version. Please upload a document instead."
                }
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete a file"""
        try:
            # Send request
            response = requests.delete(
                f"{self.documents_url}/{file_id}"
            )
            
            # Check response
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": response.json().get("message", "File deleted successfully")
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to delete file")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def list_files(self) -> Dict[str, Any]:
        """List all files"""
        try:
            # Send request
            response = requests.get(
                f"{self.documents_url}/list"
            )
            
            # Check response
            if response.status_code == 200:
                return {
                    "success": True,
                    "files": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Failed to list files")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Create API client instance
api_client = APIClient() 