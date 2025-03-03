from langchain.prompts import PromptTemplate

# Document processing prompt
DOCUMENT_PROCESSING_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""
    You are a document structure extraction system designed to convert raw text from documents into structured JSON.
    
    Analyze the following document text and extract its key information into a structured JSON format.
    Look for patterns, sections, titles, and important data points.
    
    TEXT:
    {text}
    
    Your task is to create a well-structured JSON representation of this document's content.
    Identify and include all important entities, relationships, and hierarchies.
    
    The JSON should be properly formatted and should capture the essence of the document.
    """
)

# JSON formatting prompt
JSON_FORMATTING_PROMPT = PromptTemplate(
    input_variables=["json_data"],
    template="""
    You are a JSON formatting expert. Your task is to take the following JSON data and ensure it is properly formatted.
    
    JSON DATA:
    {json_data}
    
    Please return a properly formatted JSON object that maintains the structure and content of the original data.
    If there are any errors or inconsistencies in the JSON, fix them while preserving the original intent.
    """
)

# Document type detection prompt
DOCUMENT_TYPE_DETECTION_PROMPT = PromptTemplate(
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