from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# TODO: add logger decorator and inject logger from level above
logger = logging.getLogger(__name__)

class OAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify OAuth authentication for protected routes
    """
    
    def __init__(self, app, exclude_paths=None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Check if user is authenticated via session
        user = request.session.get('user')
        
        if not user:
            # Check for OAuth token in Authorization header
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning(f"Unauthorized access attempt to {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Not authenticated"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Extract token
            token = auth_header.split(' ')[1]
            
            # Validate token (in a real app, you would verify with OAuth provider)
            try:
                # This is a placeholder for actual token validation
                # In a real implementation, you would verify the token with your OAuth provider
                # user = await validate_oauth_token(token)
                
                # For demonstration, we'll just check if token exists
                if not token:
                    raise ValueError("Invalid token")
                
                # Add user to request state for use in route handlers
                request.state.user = {"token": token}
                
            except Exception as e:
                logger.error(f"Token validation error: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid authentication credentials"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
        else:
            # User is already authenticated via session
            request.state.user = user
        
        # Proceed with the request
        return await call_next(request)