from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base

class User(Base):
    __tablename__='users'
    id:Mapped[int]=mapped_column(primary_key=True)
    username:Mapped[str]=mapped_column(unique=True)
    hashed_password:Mapped[str]
    tasks:Mapped[list['Task']]=relationship(back_populates='owner')