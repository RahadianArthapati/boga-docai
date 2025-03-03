import os
import json
import time
from typing import Dict, Any, List, Annotated, TypedDict, Literal
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


# Define state
class DocumentState(TypedDict):
    """State for document processing graph"""
    text: str
    document_type: str
    json_result: Dict[str, Any]
    error: str
    status: Literal["processing", "success", "error"]


# Define output model
class DocumentContent(BaseModel):
    """Model for document content"""
    content: Dict[str, Any] = Field(description="The structured content of the document")


class SimpleDocumentGraph:
    """Simple document processing graph"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the document graph"""
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=self.api_key
        )
        
        # Set up output parser
        self.parser = PydanticOutputParser(pydantic_object=DocumentContent)
        
        # Create graph
        self.graph = self._build_graph()
    
    def _detect_document_type(self, state: DocumentState) -> DocumentState:
        """Detect document type"""
        try:
            # Create prompt
            prompt = PromptTemplate(
                input_variables=["text"],
                template="""
                You are a document classification system. Your task is to analyze the following text and determine what type of document it is.
                
                TEXT:
                {text}
                
                Based on the content, structure, and terminology, what type of document is this?
                Examples of document types include: invoice, receipt, contract, resume, letter, report, form, etc.
                
                Please return only the document type as a single word or short phrase.
                """
            )
            
            # Run the LLM
            result = self.llm.invoke(prompt.format(text=state["text"]))
            
            # Update state
            state["document_type"] = result.content.strip()
            
            return state
            
        except Exception as e:
            state["error"] = f"Error detecting document type: {str(e)}"
            state["status"] = "error"
            return state
    
    def _extract_json(self, state: DocumentState) -> DocumentState:
        """Extract JSON from document"""
        try:
            # Create prompt
            prompt = PromptTemplate(
                input_variables=["text", "document_type", "format_instructions"],
                template="""
                You are a document structure extraction system designed to convert raw text from documents into structured JSON.
                
                The document appears to be a {document_type}.
                
                Analyze the following document text and extract its key information into a structured JSON format.
                Look for patterns, sections, titles, and important data points relevant to this type of document.
                
                {format_instructions}
                
                TEXT:
                {text}
                
                Your task is to create a well-structured JSON representation of this document's content.
                Identify and include all important entities, relationships, and hierarchies.
                """
            )
            
            # Run the LLM
            result = self.llm.invoke(
                prompt.format(
                    text=state["text"],
                    document_type=state["document_type"],
                    format_instructions=self.parser.get_format_instructions()
                )
            )
            
            # Parse JSON
            try:
                # Try to parse from the output directly
                json_result = self.parser.parse(result.content)
                structured_data = json_result.content
            except Exception:
                # Fallback: try to extract JSON directly
                try:
                    # Look for JSON in the response
                    json_start = result.content.find("{")
                    json_end = result.content.rfind("}")
                    
                    if json_start != -1 and json_end != -1:
                        json_string = result.content[json_start:json_end + 1]
                        structured_data = json.loads(json_string)
                    else:
                        structured_data = {"error": "Failed to extract JSON from LLM response"}
                except Exception as e:
                    structured_data = {"error": f"Failed to parse JSON: {str(e)}"}
            
            # Update state
            state["json_result"] = structured_data
            state["status"] = "success"
            
            return state
            
        except Exception as e:
            state["error"] = f"Error extracting JSON: {str(e)}"
            state["status"] = "error"
            return state
    
    def _handle_error(self, state: DocumentState) -> DocumentState:
        """Handle errors"""
        # Log error
        print(f"Error processing document: {state['error']}")
        
        # Return state
        return state
    
    def _should_extract_json(self, state: DocumentState) -> Literal["extract_json", "handle_error"]:
        """Decide whether to extract JSON or handle error"""
        if state["status"] == "error":
            return "handle_error"
        return "extract_json"
    
    def _should_end(self, state: DocumentState) -> Literal["end", "handle_error"]:
        """Decide whether to end or handle error"""
        if state["status"] == "error":
            return "handle_error"
        return "end"
    
    def _build_graph(self) -> StateGraph:
        """Build the graph"""
        # Create graph
        graph = StateGraph(DocumentState)
        
        # Add nodes
        graph.add_node("detect_document_type", self._detect_document_type)
        graph.add_node("extract_json", self._extract_json)
        graph.add_node("handle_error", self._handle_error)
        
        # Add edges
        graph.add_edge("detect_document_type", self._should_extract_json)
        graph.add_conditional_edges(
            "extract_json",
            self._should_end,
            {
                "end": END,
                "handle_error": "handle_error"
            }
        )
        graph.add_edge("handle_error", END)
        
        # Set entry point
        graph.set_entry_point("detect_document_type")
        
        # Compile graph
        return graph.compile()
    
    def process(self, text: str) -> Dict[str, Any]:
        """Process a document"""
        try:
            # Start timer
            start_time = time.time()
            
            # Initialize state
            state = {
                "text": text,
                "document_type": "",
                "json_result": {},
                "error": "",
                "status": "processing"
            }
            
            # Run the graph
            result = self.graph.invoke(state)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Return result
            return {
                "success": result["status"] == "success",
                "document_type": result["document_type"],
                "json_result": result["json_result"],
                "error": result["error"],
                "processing_time": processing_time
            }
                
        except Exception as e:
            return {
                "success": False,
                "document_type": "",
                "json_result": {},
                "error": str(e),
                "processing_time": 0
            }


# Create document graph instance
document_graph = SimpleDocumentGraph() 