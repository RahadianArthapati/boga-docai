import os
import json
import time
from typing import Dict, Any, Optional, List

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from backend.services.ocr_service import OCRService

# Load environment variables
load_dotenv()


class DocumentStructure(BaseModel):
    """Model for document structure"""
    content: Dict[str, Any] = Field(description="The structured content of the document")


class LLMService:
    """Service for LLM processing"""
    
    def __init__(self):
        """Initialize the LLM service"""
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=self.api_key
        )
        
        # Initialize Vision LLM
        self.vision_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=self.api_key,
            max_tokens=4096
        )
        
        # Set up output parser
        self.parser = PydanticOutputParser(pydantic_object=DocumentStructure)
        
        # Initialize prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
            template="""
            You are a document structure extraction system designed to convert raw text from documents into structured JSON.
            
            Analyze the following document text and extract its key information into a structured JSON format.
            Look for patterns, sections, titles, and important data points.
            
            {format_instructions}
            
            TEXT:
            {text}
            
            Your task is to create a well-structured JSON representation of this document's content.
            Identify and include all important entities, relationships, and hierarchies.
            """
        )
        
        # Create processing chain (modern approach)
        self.chain = self.prompt_template | self.llm
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """Process text with LLM"""
        try:
            # Start timer
            start_time = time.time()
            
            # Run the chain
            response = self.chain.invoke({"text": text})
            
            # Extract content from response
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extract and parse JSON
            structured_data = self._parse_llm_response(content)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "extracted_text": text,
                "json_result": structured_data,
                "processing_time": processing_time
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_document(self, file_id: str, file_name: str, extracted_text: str, is_image_based: bool = False, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Process a document with LLM"""
        try:
            start_time = time.time()
            
            if is_image_based and file_path:
                # Process document as an image
                result = self._process_document_image(file_path, file_id)
            else:
                # Process document as text
                result = self.process_text(extracted_text)
            
            if result["success"]:
                # Calculate processing time
                processing_time = time.time() - start_time
                
                return {
                    "success": True,
                    "file_id": file_id,
                    "file_name": file_name,
                    "extracted_text": result.get("extracted_text", extracted_text),
                    "json_result": result["json_result"],
                    "processing_time": processing_time
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_document_image(self, file_path: str, file_id: str) -> Dict[str, Any]:
        """Process a document as an image using vision capabilities"""
        try:
            # Determine file type
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                # Convert PDF to images
                base64_images = OCRService.convert_pdf_to_images(file_path)
                
                if not base64_images:
                    return {
                        "success": False,
                        "error": "Failed to convert PDF to images"
                    }
                
                # Process the first page
                return self._process_base64_image(base64_images[0])
            else:
                # Process image file
                base64_image = OCRService.convert_image_to_base64(file_path)
                
                if not base64_image:
                    return {
                        "success": False,
                        "error": "Failed to convert image to base64"
                    }
                
                return self._process_base64_image(base64_image)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing document image: {str(e)}"
            }
    
    def _process_base64_image(self, base64_image: str) -> Dict[str, Any]:
        """Process a base64-encoded image with vision model"""
        try:
            # Construct messages for vision model
            messages = [
                {
                    "role": "system",
                    "content": "You are a document analysis AI capable of extracting structured information from images. Extract all key information from the document and provide it in a well-structured JSON format."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyze this document. Extract all text content and provide it as 'extracted_text'. Then analyze the structure and content to create a well-organized JSON representation in 'json_result'. {self.parser.get_format_instructions()}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # Call the vision model
            response = self.vision_llm.invoke(messages)
            
            # Try to extract both the text and structured data from the response
            content = response.content
            
            # Extract JSON from the response
            structured_data = self._parse_llm_response(content)
            
            # Extract text content (might be in the response or in the structured data)
            extracted_text = ""
            if "extracted_text" in structured_data:
                extracted_text = structured_data.pop("extracted_text")
            else:
                # Try to extract plain text from the response
                for line in content.split("\n"):
                    if not line.strip().startswith("{") and not line.strip().startswith("}"):
                        extracted_text += line + "\n"
            
            return {
                "success": True,
                "extracted_text": extracted_text,
                "json_result": structured_data
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing image with vision model: {str(e)}"
            }
    
    def _parse_llm_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from LLM response"""
        try:
            # Try to parse from the output directly using the parser
            try:
                json_result = self.parser.parse(text)
                structured_data = json_result.content
            except Exception:
                # Fallback: try to extract JSON directly
                try:
                    # Look for JSON in the response
                    json_start = text.find("{")
                    json_end = text.rfind("}")
                    
                    if json_start != -1 and json_end != -1:
                        json_string = text[json_start:json_end + 1]
                        structured_data = json.loads(json_string)
                    else:
                        structured_data = {"error": "Failed to extract JSON from LLM response"}
                except Exception as e:
                    structured_data = {"error": f"Failed to parse JSON: {str(e)}"}
            
            return structured_data
        except Exception as e:
            return {"error": f"Error parsing LLM response: {str(e)}"}


# Create LLM service instance
llm_service = LLMService() 