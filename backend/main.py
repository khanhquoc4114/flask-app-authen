from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
import os
from dotenv import load_dotenv
import httpx
from typing import Optional, Dict, Any
from schemas import *
from routes import auth_routes
from database import engine, Base
import time
from sqlalchemy.exc import OperationalError

load_dotenv()
oauth = OAuth()

Base.metadata.create_all(bind=engine)

app = FastAPI( title="OAuth Microservice API")

# Lấy route file
app.include_router(auth_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

secret_key = os.getenv('FLASK_SECRET_KEY', "This is flask secret key")
if not secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is not set")
app.add_middleware(SessionMiddleware, secret_key=secret_key)

oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    userinfo_url='https://api.github.com/user',
    client_kwargs={'scope': 'user:email'}
)

oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    userinfo_url='https://www.googleapis.com/oauth2/v2/userinfo',
    client_kwargs={'scope': 'openid email profile'},
    redirect_uri='http://localhost:8000/auth/google/callback',
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
)

# Utility functions
def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user from session"""
    return request.session.get('user')

def login_required(request: Request):
    """Dependency to require login"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

@app.get("/", response_model=dict)
async def root():
    """API root endpoint"""
    return {
        "service": "OAuth Microservice API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": {
                "google": "/auth/google",
                "github": "/auth/github",
                "logout": "/api/auth/logout",
                "user": "/api/auth/user",
                "check": "/api/auth/check"
            },
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/auth/check", response_model=dict)
async def check_auth_status(request: Request):
    """Check if user is authenticated"""
    user = get_current_user(request)
    return {
        "authenticated": user is not None,
        "user": user if user else None
    }

@app.get("/auth/google")
async def google_auth(request: Request):
    """Initialize Google OAuth"""
    redirect_uri = f"{request.base_url}auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def google_callback(request: Request):
    """Google OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {token["access_token"]}'}
            )
            user_info = resp.json()

        if not user_info or 'id' not in user_info:
            # Redirect to frontend with error
            frontend_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/error?message=google_auth_failed"
            return RedirectResponse(url=frontend_url, status_code=302)

        # Store user in session
        user_data = {
            'id': user_info['id'],
            'name': user_info.get('name', ''),
            'email': user_info.get('email', ''),
            'picture': user_info.get('picture', ''),
            'provider': 'google'
        }
        request.session['user'] = user_data

        # Redirect to frontend with success
        frontend_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/success"
        return RedirectResponse(url=frontend_url, status_code=302)

    except Exception as e:
        print(f"[ERROR] Exception in Google callback: {e}")
        frontend_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/error?message=google_callback_error"
        return RedirectResponse(url=frontend_url, status_code=302)

@app.get("/auth/github")
async def github_auth(request: Request):
    """Initialize GitHub OAuth"""
    redirect_uri = f"{request.base_url}auth/github/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)

@app.get("/auth/github/callback")
async def github_callback(request: Request):
    """GitHub OAuth callback"""
    try:
        token = await oauth.github.authorize_access_token(request)
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                'https://api.github.com/user',
                headers={'Authorization': f'Bearer {token["access_token"]}'}
            )
            user_info = resp.json()
            
            email = None
            email_resp = await client.get(
                'https://api.github.com/user/emails',
                headers={'Authorization': f'Bearer {token["access_token"]}'}
            )
            
            if email_resp.status_code == 200:
                emails = email_resp.json()
                for email_obj in emails:
                    if email_obj.get('primary'):
                        email = email_obj.get('email')
                        break
        
        if user_info and 'id' in user_info:
            user_data = {
                'id': str(user_info['id']),
                'name': user_info.get('name') or user_info.get('login', ''),
                'email': email or '',
                'picture': user_info.get('avatar_url', ''),
                'provider': 'github',
                'username': user_info.get('login', '')
            }
            request.session['user'] = user_data
            
            # Redirect to frontend with success
            frontend_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/success"
            return RedirectResponse(url=frontend_url, status_code=302)
        else:
            frontend_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/error?message=github_auth_failed"
            return RedirectResponse(url=frontend_url, status_code=302)
            
    except Exception as e:
        print(f"Error in GitHub callback: {e}")
        import traceback
        traceback.print_exc()
        frontend_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/error?message=github_callback_error"
        return RedirectResponse(url=frontend_url, status_code=302)

@app.post("/api/auth/logout", response_model=dict)
async def api_logout(request: Request):
    """API logout endpoint"""
    request.session.pop('user', None)
    return {"success": True, "message": "Logged out successfully"}

@app.get("/api/auth/user", response_model=UserResponse)
async def api_get_user(request: Request, user: dict = Depends(login_required)):
    """API endpoint to get current user info"""
    return UserResponse(**user)

@app.get("/api/auth/providers", response_model=dict)
async def get_auth_providers():
    """Get available authentication providers"""
    base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
    return {
        "providers": [
            {
                "name": "google",
                "display_name": "Google",
                "auth_url": f"{base_url}/auth/google",
                "icon": "google"
            },
            {
                "name": "github", 
                "display_name": "GitHub",
                "auth_url": f"{base_url}/auth/github",
                "icon": "github"
            }
        ]
    }

@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc: HTTPException):
    """Handle unauthorized access - return JSON for API"""
    return JSONResponse(
        status_code=401,
        content={"success": False, "message": "Authentication required", "error_code": "UNAUTHORIZED"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle internal server errors"""
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error", "error_code": "INTERNAL_ERROR"}
    )