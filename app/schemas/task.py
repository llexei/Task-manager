from pydantic import BaseModel,Field,ConfigDict
from typing import Optional
from datetime import datetime

class TaskOut(BaseModel):
    id:int
    title:str=Field(min_length=5,max_length=20)
    description:Optional[str]=None
    is_completed:bool=False
    owner_id:int
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    title:str=Field(min_length=5,max_length=20)
    description:Optional[str]=None

class TaskUpdate(BaseModel):
    title:str=Field(None,min_length=5,max_length=20)
    description:Optional[str]=None
    is_completed:bool=False

