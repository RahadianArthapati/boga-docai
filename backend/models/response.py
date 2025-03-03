from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class UploadResponse(BaseModel):
    """Response model for file upload"""
    file_id: str = Field(..., description="ID of the uploaded file")
    file_name: str = Field(..., description="Name of the uploaded file")
    file_type: str = Field(..., description="Type of the uploaded file")
    file_size: int = Field(..., description="Size of the uploaded file in bytes")
    message: str = Field(..., description="Status message")


class ProcessingResponse(BaseModel):
    """Response model for file processing"""
    file_id: Optional[str] = Field(None, description="ID of the processed file")
    file_name: Optional[str] = Field(None, description="Name of the processed file")
    extracted_text: str = Field(..., description="Extracted text from the file")
    json_result: Dict[str, Any] = Field(..., description="Structured JSON result")
    processing_time: float = Field(..., description="Processing time in seconds")
    

class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details") 