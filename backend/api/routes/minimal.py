"""
Minimal router that doesn't depend on any complex services.
Use this for basic connectivity testing.
"""

from fastapi import APIRouter, Request
from typing import Dict, Any, List
import os
from datetime import datetime

router = APIRouter()

@router.get("/status")
async def status() -> Dict[str, Any]:
    """Basic status endpoint that doesn't require any services"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "DocAI Minimal API",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@router.get("/ping")
async def ping() -> Dict[str, str]:
    """Simple ping-pong endpoint for connection tests"""
    return {"message": "pong"}

@router.get("/env")
async def environment() -> Dict[str, Dict[str, str]]:
    """Return safe environment information"""
    
    # Only include safe environment variables
    safe_vars = {
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
        "FRONTEND_URL": os.getenv("FRONTEND_URL", "not set"),
        "UPLOAD_DIR": os.getenv("UPLOAD_DIR", "uploads"),
        "DEBUG": "true" if os.getenv("DEBUG") else "false",
        "API_VERSION": "0.1.0",
        "PYTHON_VERSION": os.getenv("PYTHON_VERSION", "unknown")
    }
    
    return {
        "environment": safe_vars
    }

@router.post("/echo")
async def echo(request: Request) -> Dict[str, Any]:
    """Echo back any JSON payload sent to this endpoint"""
    try:
        body = await request.json()
        return {
            "echo": body,
            "received_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": f"Failed to parse JSON: {str(e)}",
            "received_at": datetime.now().isoformat()
        } 