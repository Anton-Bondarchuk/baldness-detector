from authlib.integrations.starlette_client import OAuth

from fastapi import Request, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse

from app.config import google_oauth_config
from app.oauth.infra.get_db import get_db
from app.oauth.infra.pg_user_repository import PgUserRepository
from app.oauth.interfaces.http.action.auth import (
    _create_or_get_user,
    _to_dto
)

oauth = OAuth()
oauth.register(
    name="google",
    client_id=google_oauth_config.client_id,
    client_secret=google_oauth_config.client_secret.get_secret_value(),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Export google for convenience
google = oauth.google
templates = Jinja2Templates(directory="templates")


router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    google_auth_url = request.url_for("auth_callback")

    return templates.TemplateResponse(
        "index.html", {"request": request, "google_auth_url": f"/login"}
    )


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback")
async def auth_callback(request: Request, db=Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_repo = PgUserRepository(db)
        user_info = await oauth.google.userinfo(token=token)
        dto = await _to_dto(user_info)
        user_model = await _create_or_get_user(dto, user_repo)

        return {
            "message": "Authentication successful!", 
            "user_info": {
                "email": user_model.email,
                "name": user_model.name,
                "picture": user_model.picture,
                "google_id": user_model.google_id
            }
        }

    except Exception as e:
        print(f"Error in auth_callback: {e}")
        return {"error": str(e)}
