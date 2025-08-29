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
from sqlalchemy.orm import Session
from database import get_db
from models import User
from datetime import datetime
from auth import *

load_dotenv()
oauth = OAuth()

Base.metadata.create_all(bind=engine)

app = FastAPI( title="OAuth Microservice API")

# Lấy route file
app.include_router(auth_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
)

# Utility functions
def get_current_session_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user from session"""
    return request.session.get('user')

def login_required(request: Request):
    """Dependency to require login"""
    user = get_current_session_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

@app.get("/", response_model=dict)
def root():
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
    user = get_current_session_user(request)
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
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {token["access_token"]}'}
            )
            user_info = resp.json()

        if not user_info or 'id' not in user_info:
            frontend_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/error?message=google_auth_failed"
            return RedirectResponse(url=frontend_url, status_code=302)

        # 1. Kiểm tra user tồn tại trong DB
        db_user = db.query(User).filter(User.email == user_info["email"]).first()
        if not db_user:
            # 2. Nếu chưa có, tạo user mới
            db_user = User(
                email=user_info["email"],
                full_name=user_info.get("name", ""),
                hashed_password="",  # OAuth user không cần mật khẩu
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        # 3. Tạo JWT access token
        access_token = create_access_token({"sub": str(db_user.id), "email": db_user.email})

        # 4. Redirect về frontend kèm token
        frontend_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/login?token={access_token}"
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
async def github_callback(request: Request, db: Session = Depends(get_db)):
    """GitHub OAuth callback"""
    try:
        # Exchange code for access_token
        token = await oauth.github.authorize_access_token(request)

        async with httpx.AsyncClient() as client:
            # Get user profile
            resp = await client.get(
                'https://api.github.com/user',
                headers={'Authorization': f'Bearer {token["access_token"]}'}
            )
            user_info = resp.json()

            # Get primary email (GitHub có thể không trả email trong user_info)
            email = None
            email_resp = await client.get(
                'https://api.github.com/user/emails',
                headers={'Authorization': f'Bearer {token["access_token"]}'}
            )
            if email_resp.status_code == 200:
                emails = email_resp.json()
                for email_obj in emails:
                    if email_obj.get('primary') and email_obj.get('verified'):
                        email = email_obj.get('email')
                        break

        if user_info and 'id' in user_info:
            # Tìm user trong DB
            user = db.query(User).filter(User.email == email).first()

            if not user:
                user = User(
                    email=email,
                    full_name=user_info.get("name") or user_info.get("login", ""),
                    username=user_info.get("login", ""),
                    avatar=user_info.get("avatar_url", ""),
                    provider="github",
                    hashed_password=""  # GitHub login không dùng password
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            # Tạo JWT token
            access_token = create_access_token({"sub": str(user.id)})

            # Redirect về frontend
            frontend_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/login#token={access_token}"
            return RedirectResponse(url=frontend_url, status_code=302)

        else:
            frontend_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/error?message=github_auth_failed"
            return RedirectResponse(url=frontend_url, status_code=302)

    except Exception as e:
        print(f"[ERROR] GitHub callback: {e}")
        import traceback
        traceback.print_exc()
        frontend_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/error?message=github_callback_error"
        return RedirectResponse(url=frontend_url, status_code=302)

@app.post("/api/auth/logout", response_model=dict)
async def api_logout(request: Request):
    """API logout endpoint"""
    request.session.pop('user', None)
    return {"success": True, "message": "Logged out successfully"}

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