from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict, Any

from backend.models.response import UploadResponse, ErrorResponse
from backend.services.file_service import file_service
from backend.core.config import settings

router = APIRouter()


@router.post("/upload", 
             response_model=UploadResponse,
             responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file for processing
    
    - **file**: PDF or image file to upload
    
    Returns the file ID and metadata
    """
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset file position
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024 * 1024)}MB"
        )
    
    # Save file
    result = file_service.save_upload_file(file)
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to upload file")
        )
    
    # Return response
    return UploadResponse(
        file_id=result["file_id"],
        file_name=result["file_name"],
        file_type=result["file_type"],
        file_size=result["file_size"],
        message="File uploaded successfully"
    )


@router.delete("/files/{file_id}", 
               responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def delete_file(file_id: str):
    """
    Delete a file by ID
    
    - **file_id**: ID of the file to delete
    
    Returns success message
    """
    success, message = file_service.delete_file(file_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=message
        )
    
    return {"message": message} 