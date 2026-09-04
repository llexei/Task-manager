from pydantic import BaseModel

class TokenPair(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str

class RefreshRequest(BaseModel):
    refresh_token:str

class Token(BaseModel):
    access_token:str
    token_type:str
