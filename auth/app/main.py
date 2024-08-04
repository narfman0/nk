from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI

from app.db import User, db
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, fastapi_users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """App-level startup and teardown method. We need to tick world regularly,
    and this is how we do it with the current implementation."""

    await init_beanie(
        database=db,
        document_models=[
            User,
        ],
    )
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}
