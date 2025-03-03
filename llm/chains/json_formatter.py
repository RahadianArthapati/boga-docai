import os
import json
from typing import Dict, Any
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from llm.prompts.templates import JSON_FORMATTING_PROMPT

# Load environment variables
load_dotenv()


class JSONFormatter:
    """Chain for formatting JSON with LLM"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0):
        """Initialize the JSON formatter"""
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=self.api_key
        )
        
        # Create LLM chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=JSON_FORMATTING_PROMPT
        )
    
    def format(self, json_data: str) -> Dict[str, Any]:
        """Format JSON with LLM"""
        try:
            # Run the chain
            result = self.chain.invoke({"json_data": json_data})
            
            # Try to parse the result as JSON
            try:
                # Look for JSON in the response
                json_start = result["text"].find("{")
                json_end = result["text"].rfind("}")
                
                if json_start != -1 and json_end != -1:
                    json_string = result["text"][json_start:json_end + 1]
                    formatted_json = json.loads(json_string)
                else:
                    # Try to parse the entire response
                    formatted_json = json.loads(result["text"])
                    
                return {
                    "success": True,
                    "result": formatted_json
                }
                
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse JSON from LLM response"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Create JSON formatter instance
json_formatter = JSONFormatter() 