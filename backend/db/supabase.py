import os
import json
from typing import Dict, Any, List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

from backend.core.config import settings

# Load environment variables
load_dotenv()

class SupabaseClient:
    """Client for Supabase operations"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.client = self._get_client()
        
    def _get_client(self) -> Optional[Client]:
        """Get Supabase client instance"""
        if not self.url or not self.key:
            print("Warning: Supabase URL or key not set.")
            return None
        
        try:
            return create_client(self.url, self.key)
        except Exception as e:
            print(f"Error connecting to Supabase: {e}")
            return None
    
    def store_document_result(self, 
                             file_name: str, 
                             file_type: str, 
                             extracted_text: str, 
                             json_result: Dict[str, Any]) -> Dict[str, Any]:
        """Store document processing result in Supabase"""
        if not self.client:
            return {"error": "Supabase client not initialized"}
            
        try:
            # Convert JSON to string for storage
            json_str = json.dumps(json_result)
            
            # Insert record
            data, error = self.client.table("document_results").insert({
                "file_name": file_name,
                "file_type": file_type,
                "extracted_text": extracted_text,
                "json_result": json_str
            }).execute()
            
            if error:
                return {"error": str(error)}
                
            return {"success": True, "data": data}
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_document_results(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all document results from Supabase"""
        if not self.client:
            return [{"error": "Supabase client not initialized"}]
            
        try:
            data, error = self.client.table("document_results").select("*").limit(limit).execute()
            
            if error:
                return [{"error": str(error)}]
                
            # Parse JSON strings back to objects
            for item in data:
                if "json_result" in item and isinstance(item["json_result"], str):
                    item["json_result"] = json.loads(item["json_result"])
                    
            return data
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_document_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Get a document result by ID"""
        if not self.client:
            return {"error": "Supabase client not initialized"}
            
        try:
            data, error = self.client.table("document_results").select("*").eq("id", doc_id).execute()
            
            if error:
                return {"error": str(error)}
                
            if not data or len(data) == 0:
                return {"error": "Document not found"}
                
            # Parse JSON string back to object
            if "json_result" in data[0] and isinstance(data[0]["json_result"], str):
                data[0]["json_result"] = json.loads(data[0]["json_result"])
                
            return data[0]
            
        except Exception as e:
            return {"error": str(e)}

# Create Supabase client instance
supabase_client = SupabaseClient() 