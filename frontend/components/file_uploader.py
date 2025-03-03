import streamlit as st
from typing import Dict, Any, Callable, Optional

from frontend.utils.api_client import api_client


class FileUploader:
    """File uploader component"""
    
    def __init__(self):
        """Initialize file uploader"""
        self.allowed_types = ["pdf", "png", "jpg", "jpeg"]
    
    def render(self, on_upload_complete: Optional[Callable[[Dict[str, Any]], None]] = None):
        """Render file uploader component"""
        st.subheader("Upload Document")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload a PDF or image file",
            type=self.allowed_types,
            help="Supported file types: PDF, PNG, JPG, JPEG"
        )
        
        # Process uploaded file
        if uploaded_file is not None:
            # Show file info
            st.write(f"File: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            # Upload button
            if st.button("Process Document"):
                with st.spinner("Uploading file..."):
                    # Upload file
                    result = api_client.upload_file(uploaded_file)
                    
                    if "file_id" in result:
                        st.success(f"File uploaded successfully: {result['file_name']}")
                        
                        # Call callback
                        if on_upload_complete:
                            on_upload_complete(result)
                    else:
                        st.error(f"Failed to upload file: {result.get('error', 'Unknown error')}")
    
    def render_text_input(self, on_process_complete: Optional[Callable[[Dict[str, Any]], None]] = None):
        """Render text input component"""
        st.subheader("Or Enter Text Directly")
        
        # Text input
        text = st.text_area(
            "Enter document text",
            height=200,
            help="Paste text from a document to process directly"
        )
        
        # Optional file name
        file_name = st.text_input(
            "Optional file name",
            help="Enter a name for this document (optional)"
        )
        
        # Process button
        if st.button("Process Text"):
            if not text:
                st.warning("Please enter some text to process")
                return
            
            with st.spinner("Processing text..."):
                # Process text
                result = api_client.process_text(text, file_name if file_name else None)
                
                if result.get("success", False):
                    st.success("Text processed successfully")
                    
                    # Call callback
                    if on_process_complete:
                        on_process_complete(result.get("result", {}))
                else:
                    st.error(f"Failed to process text: {result.get('error', 'Unknown error')}")


# Create file uploader instance
file_uploader = FileUploader() 