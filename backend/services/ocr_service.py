import os
import base64
from PIL import Image
import PyPDF2
from pdf2image import convert_from_path
import io
from typing import Dict, Any, List, Optional


class OCRService:
    """Service for document image processing"""
    
    @staticmethod
    def process_file(file_path: str) -> Dict[str, Any]:
        """Process a file using OCR or text extraction"""
        try:
            # Get file extension
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Process based on file type
            if file_extension == '.pdf':
                # For PDFs, try to extract text directly
                extracted_text = OCRService._extract_text_from_pdf(file_path)
                
                if not extracted_text:
                    return {
                        "success": False,
                        "error": "Could not extract text from PDF"
                    }
                
                return {
                    "success": True,
                    "text": extracted_text
                }
            elif file_extension in ['.png', '.jpg', '.jpeg']:
                # For images, we can't extract text directly
                # This case should be handled by the vision-based approach
                return {
                    "success": False,
                    "error": "Image files should be processed using vision capabilities"
                }
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_extension}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def _extract_text_from_pdf(file_path: str) -> str:
        """Try to extract text directly from a PDF without OCR"""
        try:
            extracted_text = ""
            
            # Try to extract text directly
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from each page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip():
                        extracted_text += page_text + "\n\n"
            
            return extracted_text.strip()
                
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    @staticmethod
    def convert_pdf_to_images(file_path: str, max_pages: int = 3) -> List[str]:
        """Convert PDF to a list of base64-encoded images"""
        try:
            # Convert PDF to images
            images = convert_from_path(file_path, first_page=1, last_page=max_pages)
            
            # Convert images to base64
            base64_images = []
            for img in images:
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                base64_images.append(img_str)
            
            return base64_images
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return []
    
    @staticmethod
    def convert_image_to_base64(file_path: str) -> str:
        """Convert an image file to base64"""
        try:
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                return encoded_string
        except Exception as e:
            print(f"Error converting image to base64: {e}")
            return ""


# Create OCR service instance
ocr_service = OCRService() 