# Boga DocAI

A document processing application that uses OCR, LLMs, and computer vision to extract structured JSON data from PDFs and images.

## Features

- **PDF & Image Processing**: Upload PDFs and images to extract structured data
- **Vision-based Analysis**: Uses GPT-4o-mini's vision capabilities to analyze document images
- **Text Extraction**: Extracts text from PDF files automatically
- **Structured Output**: Converts documents into structured JSON format
- **Simple UI**: User-friendly Streamlit interface for easy document uploading and result viewing

## Architecture

- **Frontend**: Streamlit web application
- **Backend**: FastAPI RESTful API
- **LLM Processing**: OpenAI GPT-4o-mini model for text and vision processing
- **Document Processing**: PDF2Image and PyPDF2 for file processing

## Setup

### Prerequisites

- Python 3.9+
- Poppler (for PDF2Image)
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/boga-docai.git
   cd boga-docai
   ```

2. Run the setup script:
   ```
   python setup.py
   ```

3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

### Running the Application

1. Start the backend server:
   ```
   python run_backend.py
   ```

2. In a separate terminal, start the frontend:
   ```
   python run_frontend.py
   ```

3. Open your browser and navigate to http://localhost:8501

## Usage

1. Upload a document (PDF, JPG, PNG) using the file uploader
2. The system will process the document and extract text
3. The LLM will analyze the content and generate structured JSON
4. View the results in the application

## Project Structure

```
boga-docai/
├── backend/             # FastAPI backend
│   ├── api/             # API routes
│   ├── core/            # Core configurations
│   └── services/        # Business logic services
├── frontend/            # Streamlit frontend
│   ├── components/      # UI components
│   └── utils/           # Frontend utilities
├── uploads/             # Document storage
├── run_backend.py       # Backend runner script
├── run_frontend.py      # Frontend runner script
├── setup.py             # Setup script
└── requirements.txt     # Dependencies
```

## Dependencies

- fastapi: Web framework
- uvicorn: ASGI server
- streamlit: Frontend framework
- langchain: LLM orchestration
- openai: OpenAI API client
- pdf2image: PDF to image conversion
- PyPDF2: PDF text extraction
- pydantic: Data validation 