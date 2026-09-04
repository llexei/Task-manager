import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from redis import Redis
from jose import jwt, JWTError
from app.core.config import settings
from fastapi import status

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis:Redis,limit:int,window:int):
        super().__init__(app)
        self.redis=redis
        self.limit=limit
        self.window=window

    def _get_indentifier(self,request:Request)->str:

        auth_header=request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token=auth_header.split(' ')[1]

            try:
                payload=jwt.decode(token=token,key=settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
                user_id=payload.get('sub')

                if user_id:
                    return f'user:{user_id}'
                
            except JWTError:
                pass

        ip=request.client.host if request.client else 'unknown'
        return f'ip:{ip}'
    
    async def dispatch(self, request:Request, call_next):
        identifier=self._get_indentifier(request=request)
        key=f'rate_limit:{identifier}'

        current=self.redis.get(key)

        if current is None:
            self.redis.set(key,1,ex=self.window)
            return await call_next(request)

        current=int(current)
        if current>=self.limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={'detail':'Too many requests, try later'}
            )
        
        self.redis.incr(key)
        return await call_next(request)