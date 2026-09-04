from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
engine=create_engine(f'postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}')

SessionLocal=sessionmaker(bind=engine,expire_on_commit=False)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()