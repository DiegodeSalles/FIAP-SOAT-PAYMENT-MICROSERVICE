from motor.motor_asyncio import AsyncIOMotorClient
from src.config import settings

class MongoDBConnection:
    client: AsyncIOMotorClient = None

    @classmethod
    def get_client(cls):
        if cls.client is None:
            cls.client = AsyncIOMotorClient(
                settings.mongodb_url,
                maxPoolSize=100,
                minPoolSize=10,
                uuidRepresentation="standard"
            )
        return cls.client