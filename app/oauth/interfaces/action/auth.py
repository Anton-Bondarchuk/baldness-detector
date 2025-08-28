
from fastapi import HTTPException, status, BackgroundTasks
from authlib.integrations.httpx_client import AsyncOAuth2Client
from sqlalchemy.ext.asyncio import AsyncSession
from app.oauth.domain.models.user import User
from app.oauth.interfaces.dto.user import UserDTO
from app.oauth.interfaces.dto.auth import (
    AuthResponseDTO, GoogleAuthDTO, EmailAuthDTO, UserResponseDTO
)
from app.oauth.infra.pg_user_repository import PgUserRepository
from app.oauth.infra.jwt_auth import JWTAuth
from app.config import app_config
from app.services.wallet_service import create_wallet_background_task


async def __create_or_get_user(session: AsyncSession, user_dto: UserDTO) -> tuple[User, bool]:
    """
    Create a new user or get existing one

    Args:
        user_dto: User data transfer object

    Returns:
        Tuple of (User entity, is_new_user boolean)
    """
    user_repository = PgUserRepository(session)
    existing_user = await user_repository.get_by_email(user_dto.email)

    if existing_user:
        updated_user = await user_repository.create_or_update(user_dto)
        return updated_user, False

    if user_dto.google_id:
        existing_user = await user_repository.get_by_google_id(user_dto.google_id)
        if existing_user:
            updated_user = await user_repository.create_or_update(user_dto)
            return updated_user, False

    new_user = await user_repository.create_or_update(user_dto)
    return new_user, True


def __user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "google_id": user.google_id,
        "wallet_address": user.wallet_address,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }


async def _authenticate_with_google(session: AsyncSession, google_auth: GoogleAuthDTO, jwt_auth: JWTAuth, background_tasks: BackgroundTasks) -> AuthResponseDTO:
    """
    Authenticate user with Google OAuth token

    Args:
        session: Database session
        google_auth: Google authentication data
        jwt_auth: JWT authentication service
        background_tasks: FastAPI background tasks

    Returns:
        Authentication response with JWT token and user info

    Raises:
        HTTPException: If authentication fails
    """

    try:

        async with AsyncOAuth2Client() as client:
            resp = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {google_auth.access_token}'}
            )

            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google access token"
                )

            user_info = resp.json()

        user_dto = UserDTO(
            email=user_info['email'],
            name=user_info.get('name', ''),
            picture=user_info.get('picture'),
            google_id=user_info.get('sub')
        )

        user, is_new_user = await __create_or_get_user(session, user_dto)

        # If this is a new user and they don't have a wallet, create one in the background
        if is_new_user and not user.wallet_address:
            background_tasks.add_task(create_wallet_background_task, user.id, session)

        access_token = jwt_auth.create_access_token(user.id, user.email)

        return AuthResponseDTO(
            access_token=access_token,
            expires_in=app_config.jwt_expiration_hours * 3600,
            user=__user_to_dict(user)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google authentication failed: {str(e)}"
        )


async def _authenticate_with_email(session: AsyncSession, email_auth: EmailAuthDTO, jwt_auth: JWTAuth, background_tasks: BackgroundTasks) -> AuthResponseDTO:
        """
        Authenticate user with email (for mobile app direct registration)
        
        Args:
            session: Database session
            email_auth: Email authentication data
            jwt_auth: JWT authentication service
            background_tasks: FastAPI background tasks
            
        Returns:
            Authentication response with JWT token and user info
        """
        try:
            user_dto = UserDTO(
                email=email_auth.email,
                name=email_auth.name,
                picture=email_auth.picture
            )
            
            user, is_new_user = await __create_or_get_user(session, user_dto)
            
            # If this is a new user and they don't have a wallet, create one in the background
            if is_new_user and not user.wallet_address:
                background_tasks.add_task(create_wallet_background_task, user.id, session)
            
            access_token = jwt_auth.create_access_token(user.id, user.email)
            
            return AuthResponseDTO(
                access_token=access_token,
                expires_in=app_config.jwt_expiration_hours * 3600,
                user=__user_to_dict(user)
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email authentication failed: {str(e)}"
            )

