from os import environ

from beanie import Document
from fastapi_users.db import BeanieBaseUser
from fastapi_users_db_beanie import BeanieUserDatabase
from motor.motor_asyncio import AsyncIOMotorClient

DB_USER = environ.get("MONGODB_USER", "root")
DB_PASS = environ.get("MONGODB_PASS", "rootpass")
DB_HOST = environ.get("MONGODB_HOST", "localhost")
DB_PORT = int(environ.get("MONGODB_PORT", "27017"))
DB_NAME = environ.get("MONGODB_NAME", "nk")
DATABASE_URL = f"mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}"
client = AsyncIOMotorClient(DATABASE_URL, uuidRepresentation="standard")
db = client[DB_NAME]


# pylint: disable-next=too-many-ancestors
class User(BeanieBaseUser, Document):
    x: float | None = None
    y: float | None = None


async def get_user_db():
    yield BeanieUserDatabase(User)
