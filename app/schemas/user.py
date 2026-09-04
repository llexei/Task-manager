
from pydantic import BaseModel,Field,ConfigDict

class UserCreate(BaseModel):
    username:str
    password:str=Field(min_length=5)

class UserOut(BaseModel):
    id:int
    username:str
    model_config=ConfigDict(from_attributes=True)