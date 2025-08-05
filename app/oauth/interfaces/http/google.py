from authlib.integrations.starlette_client import OAuth

from fastapi import Request, APIRouter
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse

from app.config import google_oauth_config


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
async def auth_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        print("TOKEN STRUCTURE:", token)
        print("TOKEN KEYS:", list(token.keys()))

        # Use userinfo endpoint instead of trying to parse id_token
        user_info = await oauth.google.userinfo(token=token)
        return {"message": "Authentication successful!", "user_info": user_info}

    except Exception as e:
        print(f"Error in auth_callback: {e}")
        return {"error": str(e)}
