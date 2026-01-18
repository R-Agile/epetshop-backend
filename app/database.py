from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # These values are read from environment variables first, then .env file, then defaults
    # For Railway deployment: Set these in Railway's Variables tab
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "epet_db"
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()


class Database:
    def __init__(self):
        self.client = None
    

db = Database()


async def get_database():
    return db.client[settings.DATABASE_NAME]


async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    print(f"Connected to MongoDB at {settings.MONGODB_URL}")


async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Closed connection to MongoDB")
