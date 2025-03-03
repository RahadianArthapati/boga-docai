import streamlit as st
import os
import time
from dotenv import load_dotenv

from frontend.utils.api_client import api_client

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Boga DocAI Chat",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_results" not in st.session_state:
    st.session_state.file_results = {}

if "processing" not in st.session_state:
    st.session_state.processing = False


def handle_file_upload(uploaded_file):
    """Handle file upload and processing"""
    if uploaded_file is None:
        return None
    
    # Add a user message about the upload
    st.session_state.messages.append({"role": "user", "content": f"I'm uploading a document: {uploaded_file.name}"})
    
    # Process the file
    with st.spinner("Processing document..."):
        st.session_state.processing = True
        
        # Upload the file to the backend
        result = api_client.upload_file(uploaded_file)
        
        if result.get("success", False):
            file_id = result.get("file_id")
            st.session_state.file_results[file_id] = result
            
            # Create AI responses
            st.session_state.messages.append({"role": "assistant", "content": f"I've processed your document: **{uploaded_file.name}**"})
            
            # Show extracted data
            extracted_text = result.get("extracted_text", "")
            if extracted_text and len(extracted_text) > 300:
                short_text = extracted_text[:300] + "..."
                st.session_state.messages.append({"role": "assistant", "content": f"Here's a preview of the extracted text:\n\n{short_text}"})
            
            # Show structured data
            json_data = result.get("json_result", {})
            if json_data:
                st.session_state.messages.append({"role": "assistant", "content": f"I've extracted the following structured data from your document:\n```json\n{str(json_data)[:500]}\n```"})
            
            st.session_state.messages.append({"role": "assistant", "content": "Is there anything specific you'd like to know about this document?"})
        else:
            error = result.get("error", "Unknown error occurred")
            st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I couldn't process your document: {error}"})
            
            if "poppler" in error.lower():
                st.session_state.messages.append({"role": "assistant", "content": """It looks like Poppler is not installed. This is required for PDF processing.
                
Please install it:
- macOS: `brew install poppler`
- Ubuntu/Debian: `sudo apt-get install poppler-utils`
- Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/"""})
        
        st.session_state.processing = False


def handle_chat_input(user_input, uploaded_file=None):
    """Handle user text input and optional file attachment"""
    if not user_input and uploaded_file is None:
        return
    
    # If there's a file, process it
    if uploaded_file is not None:
        handle_file_upload(uploaded_file)
        return
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Simple response for now - this would be connected to an LLM in a full implementation
    responses = [
        "I'm analyzing your question...",
        "That's an interesting point about the document.",
        "Let me check the extracted data to answer that.",
        "Would you like to upload another document to compare?",
        "Is there anything specific you'd like me to explain about the document structure?"
    ]
    
    # Simulate thinking
    with st.spinner("Thinking..."):
        time.sleep(1)
        
    # Add AI response
    import random
    st.session_state.messages.append({"role": "assistant", "content": random.choice(responses)})


def main():
    """Main application"""
    # Sidebar
    with st.sidebar:
        st.title("Boga DocAI")
        st.markdown("""
        **Boga DocAI** lets you chat with your documents. Upload PDFs and images to extract and analyze information.
        
        ### Features
        - Chat-based interface
        - Document upload and analysis
        - Structured data extraction
        - PDF and image support
        """)
        
        # Document list
        if st.session_state.file_results:
            st.subheader("Processed Documents")
            for file_id, result in st.session_state.file_results.items():
                file_name = result.get("file_name", "Unknown")
                st.write(f"📄 {file_name}")
        
        # Reset chat button
        if st.button("Reset Chat"):
            st.session_state.messages = []
            st.session_state.file_results = {}
            st.experimental_rerun()

    # Main chat interface
    st.title("Boga DocAI Chat")
    
    # Display chat messages
    if len(st.session_state.messages) == 0:
        # Welcome message
        st.session_state.messages.append({"role": "assistant", "content": "Hi there! I'm your friendly AI assistant. How can I help you today?"})
    
    # Display all messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input and file upload
    col1, col2 = st.columns([5, 1])
    
    with col2:
        uploaded_file = st.file_uploader(
            "Upload file",
            type=["pdf", "png", "jpg", "jpeg"],
            key="file_upload",
            help="Supported file types: PDF, PNG, JPG, JPEG"
        )
    
    # Chat input
    if user_input := st.chat_input("Type your message here...", disabled=st.session_state.processing):
        handle_chat_input(user_input, uploaded_file)
        st.experimental_rerun()
    
    # Process file if uploaded without a message
    if uploaded_file and not user_input and not st.session_state.processing:
        handle_file_upload(uploaded_file)
        st.experimental_rerun()


if __name__ == "__main__":
    main() 