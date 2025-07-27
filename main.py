"""
IRIS Main Application Entry Point
Intelligent Responsive Interface System
"""

import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.server import create_app
from src.core.iris import iris_core

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting IRIS - Intelligent Responsive Interface System...")
    await iris_core.initialize()
    print("✅ IRIS is ready to assist!")
    
    yield
    
    # Shutdown
    print("🔄 IRIS is shutting down gracefully...")

def main():
    """Main application entry point"""
    # Create FastAPI app with lifespan
    app = create_app()
    app.router.lifespan_context = lifespan
    
    # Start the server
    print("🌐 Starting IRIS web server on http://localhost:8000")
    print("📖 API Documentation available at http://localhost:8000/docs")
    print("🎤 Voice test interface at http://localhost:8000/voice_interface")
    
    uvicorn.run(
        "main:create_app",  # Import string format
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info",
        factory=True
    )

if __name__ == "__main__":
    main()
