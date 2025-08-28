from fastapi import Request, APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.oauth.domain.models.user import User
from app.oauth.interfaces.dto.auth import (
    GoogleAuthDTO, EmailAuthDTO, AuthResponseDTO
)
from app.oauth.infra.pg_user_repository import PgUserRepository
from app.oauth.infra.get_db import get_db
from app.oauth.infra.get_current_user import get_current_user
from app.oauth.interfaces.action.auth import (
    _authenticate_with_google,
    _authenticate_with_email
)
from app.oauth.infra.jwt_auth import JWTAuth

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/google", response_model=AuthResponseDTO)
async def authenticate_google(
    google_auth: GoogleAuthDTO,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
    jwt_auth: JWTAuth = Depends(JWTAuth)
):
    """
    Authenticate user with Google OAuth access token
    
    This endpoint accepts a Google OAuth access token from a mobile app
    and returns a JWT token for API access.
    
    Args:
        google_auth: Google authentication data containing access_token
        background_tasks: FastAPI background tasks for wallet creation
        session: Database session
        jwt_auth: JWT authentication service
        
    Returns:
        AuthResponseDTO: JWT token and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        
        return await _authenticate_with_google(session, google_auth, jwt_auth, background_tasks)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/email", response_model=AuthResponseDTO)
async def authenticate_email(
    email_auth: EmailAuthDTO,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    jwt_auth: JWTAuth = Depends(JWTAuth)
):
    """
    Authenticate user with email and name (for direct mobile registration)
    
    This endpoint allows mobile apps to register/login users directly
    with email and name without Google OAuth.
    
    Args:
        email_auth: Email authentication data
        background_tasks: FastAPI background tasks for wallet creation
        db: Database session
        jwt_auth: JWT authentication service
        
    Returns:
        AuthResponseDTO: JWT token and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:

        return await _authenticate_with_email(db, email_auth, jwt_auth, background_tasks)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information from JWT token
    
    Returns:
        User information for the authenticated user
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "google_id": current_user.google_id,
        "wallet_address": current_user.wallet_address,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the authentication service
    """
    return {"status": "healthy", "service": "authentication"}
