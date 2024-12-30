from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
import httpx
import time
import jwt
from common import data_for_swagger
from services import auth_service

router = APIRouter(prefix='/auth', tags=["auth"])



GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID") # 구글 OAuth2.0 클라이언트 ID
GOOGLE_CLIENT_SECRET = os.getenv("CLIENT_SECRET") # 구글 OAuth2.0 클라이언트 비밀번호
REDIRECT_URL = os.getenv('REDIRECT_URL') # 구글 로그인 REDIRECT_URL
FRONTEND_URL = os.getenv('FRONTEND_URL') # 프론트 URL
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') # JWT 시크릿

# 환경변수 있는지 체크
if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URL, FRONTEND_URL, JWT_SECRET_KEY]):
    raise ValueError("Missing one or more environment variables for Google OAuth2.")

# 구글 로그인 시작
@router.get('/login', summary="구글 로그인페이지로 리다이렉션")
async def login(request: Request):
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URL}"
        f"&response_type=code"
        f"&scope=openid email profile"
    )
    return RedirectResponse(url=google_auth_url)
    
# 구글 로그인 성공후 jwt 발급
@router.get('/google/callback', include_in_schema=False)
async def callback(code: str):
    # 구글 로그인 응답 파싱
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
        user = await auth_service.find_or_create_user_by_google(id_info) # 유저 없으면 유저 생성

        # JWT 페이로드
        payload = {
            "sub": str(user.id),
            "name": user.name,
            "email": user.email,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        # JWT 생성
        jwt_token = jwt.encode(payload=payload, key=JWT_SECRET_KEY, algorithm="HS256")
    
        res = RedirectResponse(url=FRONTEND_URL)
        res.set_cookie(
            key='auth_token', 
            value=jwt_token,  
            max_age=3600,
            expires=3600,
            httponly=True,
            secure=True,
            samesite=None,
            domain='.voicevocab.store'
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'Invalid id_token: {str(e)}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# 유저 정보 받아오기
@router.get('/user-info', status_code=status.HTTP_200_OK, response_model=data_for_swagger.GetUserInfo, summary="JWT안의 유저 정보 받아오기")
async def user(current_user : Dict = Depends(auth_service.get_current_user)):
    return {
        'user': current_user
    }