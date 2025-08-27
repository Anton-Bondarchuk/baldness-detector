import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.oauth.interfaces.http import google
from app.oauth.interfaces.http.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.config import app_config
from app.detector.interfaces.http import detector


def main():
    app = FastAPI(
        title="Baldness Detection API",
        description="API for detecting baldness level from user photos with authentication",
        version="1.0.0",
        debug=app_config.debug,
    )

    # Add exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    app.add_middleware(
        SessionMiddleware, 
        secret_key=app_config.secret_key.get_secret_value()
    )

    # Configure CORS for mobile app
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this properly for production
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Include authentication router
    app.include_router(google.router)
    app.include_router(detector.router)

    @app.get("/")
    async def root():
        return {
            "message": "Baldness Detection API",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/v1/auth",
                "health": "/api/v1/auth/health"
            }
        }

    uvicorn.run(app, host=app_config.host, port=app_config.port)

main()