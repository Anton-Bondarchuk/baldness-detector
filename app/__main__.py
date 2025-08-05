import asyncio

import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.oauth.interfaces.http import google
from app.config import app_config


def main():
    app = FastAPI(
        title="Baldness Detection API",
        description="API for detecting baldness level from user photos with Google OAuth authentication",
        version="1.0.0",
        debug=False,  # Set to True for development
    )

    app.add_middleware(
        SessionMiddleware, 
        secret_key=app_config.secret_key.get_secret_value()
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(google.router)

    uvicorn.run(app, host="0.0.0.0", port=8000)

main()