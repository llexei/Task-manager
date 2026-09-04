
from typing import Annotated
from fastapi import Body, Depends, HTTPException,status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError,jwt
from sqlalchemy import select
from app.api.deps import oauth2_scheme
from app.api.deps import DbSession, get_current_user,RedisClient
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password,revoke_token,is_revoked
from app.models.user import User
from app.schemas.token import RefreshRequest, Token, TokenPair
from app.schemas.user import UserCreate, UserOut
from app.core.config import settings
import time

router=APIRouter()

@router.post('/register',response_model=UserOut,status_code=201)
def register(user_in:UserCreate,db:DbSession):

    existing_user=db.scalar(select(User).where(User.username==user_in.username))

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User has already registered!')
    
    user=User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post('/login',response_model=TokenPair)
def login(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:DbSession):

    existing_user=db.scalar(select(User).where(User.username==form_data.username))

    if not existing_user or not verify_password(form_data.password,existing_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate':'Bearer'}
        )
    
    access_token=create_access_token(data={'sub':str(existing_user.id),'usename':existing_user.username})
    refresh_token=create_refresh_token(data={'sub':str(existing_user.id),'username':existing_user.username})

    return{
        'access_token':access_token,
        'refresh_token':refresh_token,
        'token_type':'Bearer'
    }

@router.get('/me',response_model=UserOut)
def read_me(current_user:Annotated[User,Depends(get_current_user)]):

    return{
        'id':current_user.id,
        'username':current_user.username
    }

@router.delete('/logout')
def logout(redis:RedisClient,access_token:Annotated[str,Depends(oauth2_scheme)],refresh_token:str=Body(...,embed=True)):

    credental_exception=HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate token',
                headers={'WWW-Authenticate':'Bearer'}
            )
    
    try:
        payload_access=jwt.decode(access_token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        access_jti=payload_access.get('jti')
        access_exp=payload_access.get('exp')

        if access_jti and access_exp:
            revoke_token(redis=redis,token_type='access',jti=access_jti,ttl=max(access_exp-int(time.time()),0))

    except JWTError:
        pass

    try:
        payload_refresh=jwt.decode(refresh_token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        refresh_jti=payload_refresh.get('jti')
        refresh_exp=payload_refresh.get('exp')

        if refresh_jti and refresh_exp:
            revoke_token(redis=redis,token_type='refresh',jti=refresh_jti,ttl=max(refresh_exp-int(time.time()),0))

    except JWTError:
        pass

        return{
            'msg':'Successfully logged out'
        }

@router.post('/refresh',response_model=Token)
def refresh(redis:RedisClient,request:RefreshRequest,db:DbSession,access_token:Annotated[str,Depends(oauth2_scheme)]):

    credential_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate refresh token',
        headers={'WWW-Authenticate':'Bearer'}
    )

    try:
        refresh_payload=jwt.decode(request.refresh_token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        username=refresh_payload.get('username')

        if username is None:
            raise credential_exception
        
        refresh_jti=refresh_payload.get('jti')

        if is_revoked(redis=redis, token_type='refresh', jti=refresh_jti) or refresh_jti is None:
            raise credential_exception
        
    except JWTError:
        raise credential_exception
    
    user=db.scalar(select(User).where(User.username==username))

    if user is None:
        raise credential_exception
    
    try:
        access_payload=jwt.decode(access_token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        access_jti=access_payload.get('jti')
        access_exp=access_payload.get('exp')
        
        if not is_revoked(redis=redis,token_type='access',jti=access_jti):
            revoke_token(redis=redis,token_type='access',jti=access_jti,ttl=max(access_exp-int(time.time()),0))

    except JWTError:
        pass

    new_access_token=create_access_token(data={'sub':str(user.id),'username':user.username})
    
    return{
        'access_token':new_access_token,
        'token_type':'Bearer'
    }
