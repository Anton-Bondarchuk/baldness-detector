import logging
from typing import Dict, Optional
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class TokenInfo(BaseModel):
    sub: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None

async def validate_oauth_token(token: str) -> Dict:
    """
    Validate an OAuth token with the provider
    
    Args:
        token: The OAuth token to validate
        
    Returns:
        Dictionary containing user information if token is valid
        
    Raises:
        ValueError: If token is invalid
    """
    # For Google OAuth2, you would use their tokeninfo endpoint
    # This is just a placeholder implementation
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            )
            
            if response.status_code != 200:
                logger.warning(f"Token validation failed: {response.text}")
                raise ValueError("Invalid token")
            
            token_data = response.json()
            user_info = TokenInfo(**token_data)
            
            return user_info.dict()
            
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        raise ValueError(f"Token validation error: {str(e)}")