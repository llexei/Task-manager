from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth
from app.api import task
from app.core.redis import get_redis
from app.middleware.rate_limit import RateLimitMiddleware

app=FastAPI()
redis=next(get_redis())

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=['*']
)
app.add_middleware(
    RateLimitMiddleware,
    redis=redis,
    limit=5,
    window=10
)

app.include_router(auth.router,prefix='/api/v1/auth',tags=['auth'])
app.include_router(task.router,prefix='/api/v1',tags=['tasks'])

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app',reload=True)
