from os import environ

from beanie import Document, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import Field

DATABASE_URL = environ.get("MONGODB_URL")
DB_NAME = environ.get("MONGODB_NAME", "backend")
if not DATABASE_URL:
    DB_USER = environ.get("MONGODB_USER", "root")
    DB_PASS = environ.get("MONGODB_PASS", "rootpass")
    DB_HOST = environ.get("MONGODB_HOST", "localhost")
    DB_PORT = int(environ.get("MONGODB_PORT", "27017"))
    DATABASE_URL = f"mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}"
client = AsyncIOMotorClient(DATABASE_URL, uuidRepresentation="standard")
db = client[DB_NAME]


# pylint: disable-next=too-many-ancestors
class Character(Document):
    user_id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    x: float | None = None
    y: float | None = None
