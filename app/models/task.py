from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base
from datetime import datetime
from sqlalchemy import ForeignKey,UniqueConstraint,func

class Task(Base):
    __tablename__='tasks'
    __table_args__=(
        UniqueConstraint('owner_id','title',name='uq_owner_title'),
    )
    id:Mapped[int]=mapped_column(primary_key=True)
    title:Mapped[str]
    description:Mapped[str]=mapped_column(nullable=True,default=None)
    is_completed:Mapped[bool]=mapped_column(default=False)
    owner_id:Mapped[int]=mapped_column(ForeignKey('users.id'))
    owner:Mapped['User']=relationship(back_populates='tasks')
    created_at:Mapped[datetime]=mapped_column(server_default=func.now())