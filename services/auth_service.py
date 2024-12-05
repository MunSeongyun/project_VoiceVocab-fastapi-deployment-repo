from typing import Dict
from fastapi import HTTPException, status, Request
from sqlmodel import Session, select
from DB import connection, models
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

async def find_or_create_user_by_google(payload:Dict[str,str|int|bool]):
    with Session(connection.engine) as session:
        statement = select(models.User).where(models.User.google_id == payload['sub'])
        user = session.exec(statement=statement).first()
    if(not user):
        user = await create_user(payload)
    return user
    
async def create_user(payload:Dict[str,str|int|bool]):
    with Session(connection.engine) as session:
        new_user = models.User(name=payload['name'], google_id=payload['sub'], email=payload['email'])
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    return new_user
    
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(request: Request):
    token = request.cookies.get('auth_token')
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token"
        )
    
    payload = verify_jwt_token(token)
    return payload