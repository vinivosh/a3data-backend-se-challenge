from fastapi import APIRouter

from api.routes import (
    login,
    users,
    patients,
)

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    patients.router, prefix="/patients", tags=["patients"]
)
