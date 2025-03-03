import sys
import os
from pathlib import Path

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for critical environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key or openai_api_key == "your_openai_api_key":
    print("⚠️ WARNING: No OPENAI_API_KEY found in environment variables.")
    print("LLM features will not work correctly. Please set this in your .env file.")

# Import minimal router that doesn't depend on any external services
try:
    from backend.api.routes.minimal import router as minimal_router
    has_minimal_router = True
except ImportError as e:
    print(f"❌ Error importing minimal router: {e}")
    has_minimal_router = False

# Try to import document-related routes that depend on external services
try:
    from backend.api.routes import documents
    has_document_routes = True
except ImportError as e:
    print(f"❌ Error importing document routes: {e}")
    print("This could be due to missing dependencies or environment variables.")
    has_document_routes = False

# Create FastAPI app
app = FastAPI(
    title="Boga DocAI API",
    description="API for processing documents with OCR and LLMs",
    version="0.1.0",
)

# Configure CORS - allow multiple frontend URLs
allowed_origins = [
    "http://localhost:3000",          # Next.js default
    "http://127.0.0.1:3000",          # Next.js via IP
    "http://localhost:8501",          # Original Streamlit
    "http://localhost:5173",          # Vite development server
    "*",                              # Allow all in development
]

# Add any additional origins from environment
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

# Remove empty strings from the list
allowed_origins = [origin for origin in allowed_origins if origin]

print(f"Allowing CORS from origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health check that doesn't depend on other modules
@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Boga DocAI API is running"}

# Include minimal router for basic connectivity testing
if has_minimal_router:
    app.include_router(minimal_router, prefix="/api/v1/minimal", tags=["Minimal"])
    print("✅ Successfully loaded minimal routes")

# Include document routers, but only if they were successfully imported
if has_document_routes:
    try:
        app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
        print("✅ Successfully loaded document routes")
    except Exception as e:
        print(f"❌ Error including document routes: {e}")

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000
    print(f"Starting server at http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True) 