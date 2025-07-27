"""IRIS Main Application Entry Point""" 

import asyncio 
from src.api.server import create_app 
import uvicorn 

if __name__ == "__main__": 
    app = create_app() 
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 
