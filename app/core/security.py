from fastapi import Depends
from passlib.context import CryptContext
from datetime import timedelta,timezone,datetime
import uuid
from app.core.config import settings
from jose import jwt
from redis import Redis
from app.core.redis import get_redis

pwd_context=CryptContext(schemes=['bcrypt'],deprecated='auto')

def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    return pwd_context.verify(plain_password,hashed_password)

def create_token(data:dict,expires_delta:timedelta)->str:
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+expires_delta
    to_encode.update({'exp':expire,'jti':str(uuid.uuid4())})
    
    return jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def create_access_token(data:dict)->str:
    return create_token(data=data,expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

def create_refresh_token(data:dict)->str:
    return create_token(data=data,expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

def revoke_token(redis:Redis,token_type:str,jti:str,ttl:int):
    return redis.set(f'revoked:{token_type}:{jti}','1',ex=ttl)

def is_revoked(redis:Redis,token_type:str,jti:str)->bool:
    return redis.exists(f'revoked:{token_type}:{jti}') == 1

