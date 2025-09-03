from fastapi import Request, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.oauth.interfaces.dto.auth import (
    GoogleAuthDTO, EmailAuthDTO, AuthResponseDTO
)
from app.oauth.domain.services.auth_service import AuthService
from app.oauth.infra.pg_user_repository import PgUserRepository
from app.oauth.infra.get_db import get_db
from app.oauth.infra.get_current_user import get_current_user

router = APIRouter()

@router.post("/auth/google", response_model=AuthResponseDTO)
async def authenticate_google(
    google_auth: GoogleAuthDTO,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user with Google OAuth access token
    
    This endpoint accepts a Google OAuth access token from a mobile app
    and returns a JWT token for API access.
    
    Args:
        google_auth: Google authentication data containing access_token
        db: Database session
        
    Returns:
        AuthResponseDTO: JWT token and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        user_repository = PgUserRepository(db)
        auth_service = AuthService(user_repository)
        
        result = await auth_service.authenticate_with_google(google_auth)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/auth/email", response_model=AuthResponseDTO)
async def authenticate_email(
    email_auth: EmailAuthDTO,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user with email and name (for direct mobile registration)
    
    This endpoint allows mobile apps to register/login users directly
    with email and name without Google OAuth.
    
    Args:
        email_auth: Email authentication data
        db: Database session
        
    Returns:
        AuthResponseDTO: JWT token and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        user_repository = PgUserRepository(db)
        auth_service = AuthService(user_repository)
        
        result = await auth_service.authenticate_with_email(email_auth)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@router.get("/auth/me")
async def get_current_user(
    current_user=Depends(get_current_user)
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
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

@router.get("/auth/health")
async def health_check():
    """
    Health check endpoint for the authentication service
    """
    return {"status": "healthy", "service": "authentication"}
