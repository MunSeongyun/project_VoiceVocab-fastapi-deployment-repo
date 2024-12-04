from dotenv import load_dotenv
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import httpx
import time
import jwt

router = APIRouter(prefix='/auth')

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URL = os.getenv('REDIRECT_URL')
FRONTEND_URL = os.getenv('FRONTEND_URL')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

@router.get('/login')
async def login(request: Request):
    google_auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={REDIRECT_URL}&response_type=code&scope=openid email profile"
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
        id_info = id_token.verify_oauth2_token(id_token_value, requests.Request(), GOOGLE_CLIENT_ID)
        
        payload = {
            "sub": id_info["sub"],
            "name": id_info["name"],
            "email": id_info["email"],
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        jwt_token = jwt.encode(payload=payload,key=JWT_SECRET_KEY, algorithm="HS256")
    
        res =  RedirectResponse(f'{FRONTEND_URL}')
        res.set_cookie(
            key='auth_token', 
            value=jwt_token,  
            samesite='none', 
            max_age=3600,
            expires=3600
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'Invalid id_token: {str(e)}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")