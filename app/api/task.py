from fastapi import APIRouter,Depends,HTTPException,status
from app.api.deps import DbSession,get_current_user
from app.models.user import User
from sqlalchemy import select,func
from sqlalchemy.exc import IntegrityError
from app.models.task import Task
from typing import Annotated
from app.schemas.task import TaskCreate,TaskOut,TaskUpdate
from datetime import datetime,timezone

router=APIRouter()

Current_user=Annotated[User,Depends(get_current_user)]

@router.get('/stats')
def get_stats(db:DbSession,current_user:Current_user):
    id_active:list=db.scalars(select(Task.id).where(Task.owner_id==current_user.id,Task.is_completed==False)).all()
    id_completed:list=db.scalars(select(Task.id).where(Task.owner_id==current_user.id,Task.is_completed==True)).all()
    return{
        "total":{
            'count': len(id_completed)+len(id_active),
            'ids': sorted(id_completed+id_active)
        },
        "completed":{
            'count':len(id_completed),
            'ids':sorted(id_completed)
        },
        "active":{
            'count':len(id_active),
            'ids':sorted(id_active)
        }
    }

@router.get('/tasks',response_model=list[TaskOut])
def get_all_tasks( 
        db:DbSession,
        current_user:Current_user,
        is_completed:bool|None=None,
        limit:int=10,
        offset:int=0,
        search:str|None=None,
        order_by:str="created_at",
        order:str="desc"
    ):
    allowed_order_by={
        "created_at","title","is_completed"
    }
    allowed_order={
        "desc","asc"
    }
    req=select(Task).where(Task.owner_id==current_user.id)

    if is_completed:
        req=req.where(Task.is_completed==is_completed)
    if search:
        req=req.where(Task.title.ilike(f'%{search}%'))

    if order_by not in allowed_order_by:
        order_by='created_at'

    column=getattr(Task,order_by)

    if order not in allowed_order:
        order="desc"
    if order=="desc":
        req=req.order_by(column.desc())
    else:
        req=req.order_by(column.asc())

    req=req.offset(offset).limit(limit)

    return db.scalars(req).all()

@router.get('/tasks/{task_id}',response_model=TaskOut)
def get_task(db:DbSession,current_user:Current_user,task_id:int):

    task=db.scalar(select(Task).where(Task.owner_id==current_user.id,Task.id==task_id))

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Task not found')
    
    return task


@router.post('/tasks',response_model=TaskOut)
def create_task( db:DbSession,current_user:Current_user,task_in:TaskCreate):

    existing_task=db.scalar(select(Task).where(Task.owner_id==current_user.id,Task.title==task_in.title))

    if existing_task:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='Task with this title has already created')
    
    task=Task(
        title=task_in.title,
        description=task_in.description,
        owner_id=current_user.id,
        created_at=datetime.now(timezone.utc)
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task

@router.delete('/tasks/{task_id}',status_code=201)
def delete_task(db:DbSession, task_id:int, current_user:Current_user,):

    task=db.scalar(select(Task).where(Task.owner_id==current_user.id, Task.id==task_id))

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Task not found')
    
    db.delete(task)
    db.commit()

    return {
        'message':'Task successfuly delete'
    }

@router.patch('/tasks/{task_id}',response_model=TaskOut)
def update_task(db:DbSession,current_user:Current_user, task_id:int,task_in:TaskUpdate):

    task=db.scalar(select(Task).where(Task.owner_id==current_user.id,Task.id==task_id))

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Task not found')
    
    data=task_in.model_dump(exclude_unset=True)
    for k,v in data.items():
        setattr(task,k,v)

    try:
        db.commit()

    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Task with this title has already created')
    
    db.refresh(task)
    
    return task
