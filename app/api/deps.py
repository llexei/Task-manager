from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException,status
from jose import JWTError, jwt
from typing import Annotated
from app.models.user import User
from app.core.config import settings
from app.db.session import get_db
from sqlalchemy.orm import Session
from redis import Redis
from app.core.redis import get_redis
from app.core.security import is_revoked

oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')
DbSession=Annotated[Session,Depends(get_db)]
RedisClient=Annotated[Redis,Depends(get_redis)]


def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db:DbSession,redis:RedisClient):
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not valide credentials',
        headers={'WWW-Authenticate':'Bearer'}
    )

    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        sub=payload.get('sub')
        if sub is None:
            raise credentials_exception
        
        user_id=int(sub)

    except (JWTError,ValueError):
        raise credentials_exception
    
    ##BlackList##
    jti=payload.get('jti')
    if jti is not None and is_revoked(redis=redis,token_type='access',jti=jti):
        raise credentials_exception
    
    user=db.get(User,user_id)
    if user is None:
        raise credentials_exception
    
    return user