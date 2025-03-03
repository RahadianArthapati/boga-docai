import os
from typing import Dict, Any
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from llm.prompts.templates import DOCUMENT_PROCESSING_PROMPT

# Load environment variables
load_dotenv()

class DocumentContent(BaseModel):
    """Model for document content"""
    content: Dict[str, Any] = Field(description="The structured content of the document")


class DocumentProcessor:
    """Chain for processing documents with LLM"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0):
        """Initialize the document processor"""
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=self.api_key
        )
        
        # Set up output parser
        self.parser = PydanticOutputParser(pydantic_object=DocumentContent)
        
        # Create LLM chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=DOCUMENT_PROCESSING_PROMPT
        )
    
    def process(self, text: str) -> Dict[str, Any]:
        """Process text with LLM"""
        try:
            # Run the chain
            result = self.chain.invoke({"text": text})
            
            # Return the result
            return {
                "success": True,
                "result": result["text"]
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Create document processor instance
document_processor = DocumentProcessor() 