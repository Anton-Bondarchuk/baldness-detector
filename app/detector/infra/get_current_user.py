from fastapi import Depends, HTTPException, status, Request

async def get_current_user(request: Request):
    """
    Dependency to verify user is authenticated via Google OAuth
    """
    user = request.session.get('user')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user