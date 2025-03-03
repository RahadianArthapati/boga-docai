from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from backend.models.request import ProcessFileRequest, ProcessTextRequest
from backend.models.response import ProcessingResponse, ErrorResponse
from backend.services.file_service import file_service
from backend.services.ocr_service import ocr_service
from backend.services.llm_service import llm_service
from backend.db.supabase import supabase_client

router = APIRouter()


@router.post("/process/file", 
             response_model=ProcessingResponse,
             responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def process_file(request: ProcessFileRequest):
    """
    Process a file with OCR and LLM
    
    - **file_id**: ID of the uploaded file to process
    - **file_type**: Type of file (pdf, image)
    - **options**: Additional processing options (optional)
    
    Returns the extracted text and structured JSON
    """
    # Process file with OCR
    ocr_result = ocr_service.process_file(request.file_id)
    
    if not ocr_result.get("success", False):
        raise HTTPException(
            status_code=404 if "not found" in ocr_result.get("error", "").lower() else 400,
            detail=ocr_result.get("error", "Failed to process file with OCR")
        )
    
    # Process text with LLM
    llm_result = llm_service.process_document(
        file_id=request.file_id,
        file_name=ocr_result.get("file_name", ""),
        extracted_text=ocr_result.get("extracted_text", "")
    )
    
    if not llm_result.get("success", False):
        raise HTTPException(
            status_code=400,
            detail=llm_result.get("error", "Failed to process text with LLM")
        )
    
    # Store result in Supabase
    if supabase_client.client:
        supabase_client.store_document_result(
            file_name=ocr_result.get("file_name", ""),
            file_type=ocr_result.get("file_type", ""),
            extracted_text=ocr_result.get("extracted_text", ""),
            json_result=llm_result.get("json_result", {})
        )
    
    # Return response
    return ProcessingResponse(
        file_id=request.file_id,
        file_name=ocr_result.get("file_name", ""),
        extracted_text=ocr_result.get("extracted_text", ""),
        json_result=llm_result.get("json_result", {}),
        processing_time=llm_result.get("processing_time", 0.0)
    )


@router.post("/process/text", 
             response_model=ProcessingResponse,
             responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def process_text(request: ProcessTextRequest):
    """
    Process raw text with LLM
    
    - **text**: Raw text to process
    - **file_name**: Original file name (optional)
    - **options**: Additional processing options (optional)
    
    Returns the structured JSON
    """
    # Process text with LLM
    llm_result = llm_service.process_text(request.text)
    
    if not llm_result.get("success", False):
        raise HTTPException(
            status_code=400,
            detail=llm_result.get("error", "Failed to process text with LLM")
        )
    
    # Store result in Supabase
    if supabase_client.client and request.file_name:
        supabase_client.store_document_result(
            file_name=request.file_name,
            file_type="text",
            extracted_text=request.text,
            json_result=llm_result.get("json_result", {})
        )
    
    # Return response
    return ProcessingResponse(
        file_name=request.file_name,
        extracted_text=request.text,
        json_result=llm_result.get("json_result", {}),
        processing_time=llm_result.get("processing_time", 0.0)
    ) 