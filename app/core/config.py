from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file='.env',extra='ignore')

    DB_USER:str
    DB_NAME:str
    DB_PASSWORD:str
    DB_HOST:str
    DB_PORT:str
    REDIS_HOST:str
    REDIS_PORT:str
    REDIS_DB:str
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    REFRESH_TOKEN_EXPIRE_DAYS:int


settings=Settings()