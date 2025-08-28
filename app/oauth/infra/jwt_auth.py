from datetime import datetime, timedelta, UTC
from typing import Optional
import jwt
from app.config import app_config

class JWTAuth:
    @staticmethod
    def create_access_token(user_id: int, email: str, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a new JWT access token for the user
        
        Args:
            user_id: The user's database ID
            email: The user's email address
            expires_delta: Optional custom expiration time
            
        Returns:
            JWT token string
        """
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(hours=app_config.jwt_expiration_hours)

        to_encode = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.datetime.now(datetime.UTC)
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            app_config.jwt_secret_key.get_secret_value(),
            algorithm=app_config.jwt_algorithm
        )
        
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                app_config.jwt_secret_key.get_secret_value(),
                algorithms=[app_config.jwt_algorithm]
            )
            return payload
        except jwt.PyJWTError:
            return None
