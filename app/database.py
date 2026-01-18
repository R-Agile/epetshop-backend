from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Removing the default "localhost" forces Pydantic to find the Railway variable
    MONGODB_URL: str 
    DATABASE_NAME: str = "epet_db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    FRONTEND_URL: str = "http://localhost:5173"

    # Modern Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # Prevents crashing if Railway adds unexpected variables
    )

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
