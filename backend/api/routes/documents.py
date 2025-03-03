from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, Any, List

from backend.services.file_service import FileService

router = APIRouter()

@router.post("/upload", response_model=Dict[str, Any])
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and process a document.
    
    Takes a file upload, saves it, and processes it with OCR and/or LLM.
    Returns the extracted content and structured data.
    """
    # Process the file using FileService
    result = await FileService.process_file(file)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/list", response_model=List[Dict[str, Any]])
async def list_documents() -> List[Dict[str, Any]]:
    """
    List all uploaded documents.
    
    Returns a list of document metadata for all uploaded files.
    """
    return FileService.get_file_list()

@router.delete("/{file_id}", response_model=Dict[str, Any])
async def delete_document(file_id: str) -> Dict[str, Any]:
    """
    Delete a document by ID.
    
    Takes a file ID and deletes the associated file.
    Returns a success message or error details.
    """
    result = FileService.delete_file(file_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result 