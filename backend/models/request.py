from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ProcessFileRequest(BaseModel):
    """Request model for processing a file"""
    file_id: str = Field(..., description="ID of the uploaded file to process")
    file_type: str = Field(..., description="Type of file (pdf, image)")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Additional processing options")


class ProcessTextRequest(BaseModel):
    """Request model for processing raw text"""
    text: str = Field(..., description="Raw text to process")
    file_name: Optional[str] = Field(None, description="Original file name")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Additional processing options") 