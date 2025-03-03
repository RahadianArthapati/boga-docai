import streamlit as st
import json
from typing import Dict, Any, Optional


class ResultsView:
    """Results view component"""
    
    def render(self, result: Optional[Dict[str, Any]] = None):
        """Render results view component"""
        if not result:
            return
        
        st.subheader("Processing Results")
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["JSON Result", "Extracted Text", "Raw Data"])
        
        with tab1:
            self._render_json_result(result)
        
        with tab2:
            self._render_extracted_text(result)
        
        with tab3:
            self._render_raw_data(result)
    
    def _render_json_result(self, result: Dict[str, Any]):
        """Render JSON result"""
        st.subheader("Structured JSON")
        
        # Get JSON result
        json_result = result.get("json_result", {})
        
        if not json_result:
            st.warning("No JSON result available")
            return
        
        # Display JSON
        st.json(json_result)
        
        # Download button
        json_str = json.dumps(json_result, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"{result.get('file_name', 'document')}_result.json",
            mime="application/json"
        )
    
    def _render_extracted_text(self, result: Dict[str, Any]):
        """Render extracted text"""
        st.subheader("Extracted Text")
        
        # Get extracted text
        extracted_text = result.get("extracted_text", "")
        
        if not extracted_text:
            st.warning("No extracted text available")
            return
        
        # Display text
        st.text_area(
            "Text extracted from document",
            value=extracted_text,
            height=400,
            disabled=True
        )
        
        # Download button
        st.download_button(
            label="Download Text",
            data=extracted_text,
            file_name=f"{result.get('file_name', 'document')}_text.txt",
            mime="text/plain"
        )
    
    def _render_raw_data(self, result: Dict[str, Any]):
        """Render raw data"""
        st.subheader("Raw Data")
        
        # Display processing time
        processing_time = result.get("processing_time", 0)
        st.metric("Processing Time", f"{processing_time:.2f} seconds")
        
        # Display file info
        if "file_id" in result:
            st.write(f"File ID: {result['file_id']}")
        
        if "file_name" in result:
            st.write(f"File Name: {result['file_name']}")
        
        # Display raw JSON
        st.code(json.dumps(result, indent=2), language="json")


# Create results view instance
results_view = ResultsView() 