from typing import Dict
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request, HTTPException, Response
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
import httpx
import time
import jwt
from services import auth_service

router = APIRouter(prefix='/auth')

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URL = os.getenv('REDIRECT_URL')
FRONTEND_URL = os.getenv('FRONTEND_URL')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URL, FRONTEND_URL, JWT_SECRET_KEY]):
    raise ValueError("Missing one or more environment variables for Google OAuth2.")

@router.get('/login')
async def login(request: Request):
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URL}"
        f"&response_type=code"
        f"&scope=openid email profile"
    )
    return RedirectResponse(url=google_auth_url)
    
@router.get('/google/callback')
async def callback(code: str):
    token_request_uri = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': REDIRECT_URL,
        'grant_type': 'authorization_code',
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_request_uri, data=data)
        response.raise_for_status()
        token_response = response.json()

    id_token_value = token_response.get('id_token')
    if not id_token_value:
        raise HTTPException(status_code=400, detail="Missing id_token in response.")
    
    try:
        id_info = id_token.verify_oauth2_token(id_token_value, google_requests.Request(), GOOGLE_CLIENT_ID)
        user = await auth_service.find_or_create_user_by_google(id_info)

        payload = {
            "sub": str(user.id),
            "name": user.name,
            "email": user.email,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        jwt_token = jwt.encode(payload=payload, key=JWT_SECRET_KEY, algorithm="HS256")
    
        res = RedirectResponse(url=r'http://action-practice-bapull.s3-website.ap-northeast-2.amazonaws.com/')
        res.set_cookie(
            key='auth_token', 
            value=jwt_token,  
            max_age=3600,
            expires=3600,
            httponly=True,
            secure=True
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'Invalid id_token: {str(e)}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get('/user-info')
async def user(current_user : Dict = Depends(auth_service.get_current_user)):
    return {
        'user': current_user
    }