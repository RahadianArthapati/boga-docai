import os
import uuid
import shutil
import logging
from typing import Dict, Any, List, Optional
from fastapi import UploadFile
from werkzeug.utils import secure_filename

from backend.core.config import settings
from backend.services.ocr_service import OCRService
from backend.services.llm_service import llm_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileService:
    """Service for file operations"""
    
    @staticmethod
    async def process_file(file: UploadFile) -> Dict[str, Any]:
        """Process file upload"""
        # Log file details
        logger.info(f"Processing file: {file.filename} (content_type: {file.content_type})")
        
        # Check if file is valid
        if not FileService._is_valid_file(file):
            error_msg = f"Invalid file type. Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        
        try:
            # Generate a unique file ID
            file_id = str(uuid.uuid4())
            
            # Get secure filename
            original_filename = file.filename
            secure_name = secure_filename(original_filename) if original_filename else f"{file_id}.pdf"
            logger.info(f"Secure filename: {secure_name}")
            
            # Create file path
            file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{secure_name}")
            logger.info(f"Saving file to: {file_path}")
            
            # Ensure upload directory exists
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Log successful file save
            logger.info(f"File saved successfully: {file_path}")
            
            # Determine processing approach based on file type
            file_extension = os.path.splitext(secure_name)[1].lower()
            logger.info(f"File extension: {file_extension}")
            
            is_image_based = file_extension in ['.pdf', '.png', '.jpg', '.jpeg']
            
            # Use OCR only for text extraction if we're not using the image-based approach
            if not is_image_based:
                logger.info("Using OCR for text extraction")
                # Use OCR service to extract text
                ocr_result = OCRService.process_file(file_path)
                
                if not ocr_result["success"]:
                    logger.error(f"OCR processing failed: {ocr_result.get('error', 'Unknown error')}")
                    return ocr_result
                
                extracted_text = ocr_result["text"]
            else:
                logger.info("Using image-based approach, bypassing OCR")
                # For image-based approach, we'll just pass empty text and let LLM service handle it
                extracted_text = ""
            
            # Process with LLM
            logger.info(f"Processing with LLM (is_image_based: {is_image_based})")
            llm_result = llm_service.process_document(
                file_id=file_id,
                file_name=secure_name,
                extracted_text=extracted_text,
                is_image_based=is_image_based,
                file_path=file_path
            )
            
            # Log LLM processing result
            if llm_result["success"]:
                logger.info("LLM processing successful")
            else:
                logger.error(f"LLM processing failed: {llm_result.get('error', 'Unknown error')}")
            
            return llm_result
            
        except Exception as e:
            logger.exception(f"Error processing file: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def _is_valid_file(file: UploadFile) -> bool:
        """Check if file is valid"""
        if not file.filename:
            logger.error("Missing filename")
            return False
            
        # Get file extension
        ext = os.path.splitext(file.filename)[1].lower()
        ext_without_dot = ext[1:] if ext.startswith('.') else ext
        logger.info(f"Checking file extension: {ext} (without dot: {ext_without_dot})")
        
        # Check if extension is allowed
        is_valid = ext_without_dot in settings.ALLOWED_EXTENSIONS
        if not is_valid:
            logger.error(f"Invalid extension: {ext}. Allowed: {settings.ALLOWED_EXTENSIONS}")
        return is_valid
    
    @staticmethod
    def get_file_list() -> List[Dict[str, Any]]:
        """Get list of files in upload directory"""
        try:
            # Ensure upload directory exists
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            
            # Get list of files
            files = []
            for filename in os.listdir(settings.UPLOAD_DIR):
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                
                # Only include files, not directories
                if os.path.isfile(file_path):
                    # Extract file ID (if present)
                    file_id = filename.split('_')[0] if '_' in filename else None
                    
                    # Get file size
                    file_size = os.path.getsize(file_path)
                    
                    # Get file extension
                    ext = os.path.splitext(filename)[1].lower()
                    
                    # Add file to list
                    files.append({
                        "id": file_id,
                        "name": filename,
                        "size": file_size,
                        "extension": ext
                    })
            
            logger.info(f"Found {len(files)} files in uploads directory")
            return files
            
        except Exception as e:
            logger.exception(f"Error listing files: {str(e)}")
            return []
    
    @staticmethod
    def delete_file(file_id: str) -> Dict[str, Any]:
        """Delete file by ID"""
        try:
            # Ensure upload directory exists
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            
            # Find file by ID
            for filename in os.listdir(settings.UPLOAD_DIR):
                if filename.startswith(f"{file_id}_"):
                    file_path = os.path.join(settings.UPLOAD_DIR, filename)
                    
                    # Delete file
                    os.remove(file_path)
                    logger.info(f"Deleted file: {file_path}")
                    
                    return {
                        "success": True,
                        "file_id": file_id
                    }
            
            # File not found
            logger.error(f"File with ID {file_id} not found")
            return {
                "success": False,
                "error": f"File with ID {file_id} not found"
            }
                
        except Exception as e:
            logger.exception(f"Error deleting file: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Create file service instance
file_service = FileService() 