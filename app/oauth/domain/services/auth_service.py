from typing import Optional, Union
from fastapi import HTTPException, status
from authlib.integrations.httpx_client import AsyncOAuth2Client

from app.oauth.domain.models.user import User
from app.oauth.interfaces.dto.user import UserDTO
from app.oauth.interfaces.dto.auth import (
    GoogleAuthDTO, EmailAuthDTO, AuthResponseDTO, UserResponseDTO
)
from app.oauth.infra.pg_user_repository import PgUserRepository
from app.oauth.infra.jwt_auth import JWTAuth
from app.config import google_oauth_config, app_config

class AuthService:
    def __init__(self, user_repository: PgUserRepository):
        self.user_repository = user_repository
        self.jwt_auth = JWTAuth()

    async def authenticate_with_google(self, google_auth: GoogleAuthDTO) -> AuthResponseDTO:
        """
        Authenticate user with Google OAuth token
        
        Args:
            google_auth: Google authentication data
            
        Returns:
            Authentication response with JWT token and user info
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            # Verify Google token and get user info
            user_info = await self._verify_google_token(google_auth.access_token)
            
            # Create or update user
            user_dto = UserDTO(
                email=user_info['email'],
                name=user_info.get('name', ''),
                picture=user_info.get('picture'),
                google_id=user_info.get('sub')
            )
            
            user = await self._create_or_get_user(user_dto)
            
            # Generate JWT token
            access_token = self.jwt_auth.create_access_token(user.id, user.email)
            
            return AuthResponseDTO(
                access_token=access_token,
                expires_in=app_config.jwt_expiration_hours * 3600,
                user=self._user_to_dict(user)
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Google authentication failed: {str(e)}"
            )

    async def authenticate_with_email(self, email_auth: EmailAuthDTO) -> AuthResponseDTO:
        """
        Authenticate user with email (for mobile app direct registration)
        
        Args:
            email_auth: Email authentication data
            
        Returns:
            Authentication response with JWT token and user info
        """
        try:
            # Create user DTO
            user_dto = UserDTO(
                email=email_auth.email,
                name=email_auth.name,
                picture=email_auth.picture
            )
            
            user = await self._create_or_get_user(user_dto)
            
            # Generate JWT token
            access_token = self.jwt_auth.create_access_token(user.id, user.email)
            
            return AuthResponseDTO(
                access_token=access_token,
                expires_in=app_config.jwt_expiration_hours * 3600,
                user=self._user_to_dict(user)
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email authentication failed: {str(e)}"
            )

    async def _verify_google_token(self, access_token: str) -> dict:
        """
        Verify Google access token and fetch user info
        
        Args:
            access_token: Google access token
            
        Returns:
            User information from Google
        """
        async with AsyncOAuth2Client() as client:
            resp = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google access token"
                )
            
            return resp.json()

    async def _create_or_get_user(self, user_dto: UserDTO) -> User:
        """
        Create a new user or get existing one
        
        Args:
            user_dto: User data transfer object
            
        Returns:
            User entity
        """
        # Check if user exists by email
        existing_user = await self.user_repository.get_by_email(user_dto.email)
        
        if existing_user:
            # Update existing user with new information
            return await self.user_repository.create_or_update(user_dto)
        
        # Check if user exists by Google ID (if provided)
        if user_dto.google_id:
            existing_user = await self.user_repository.get_by_google_id(user_dto.google_id)
            if existing_user:
                return await self.user_repository.create_or_update(user_dto)
        
        # Create new user
        return await self.user_repository.create_or_update(user_dto)

    def _user_to_dict(self, user: User) -> dict:
        """Convert User entity to dictionary"""
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
            "google_id": user.google_id,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
