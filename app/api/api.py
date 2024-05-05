from fastapi import APIRouter

from app.api.endpoints import (
    auth,
    role,
    user,
    permission,
)


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(role.router, prefix="/roles", tags=["roles"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(
    permission.router, prefix="/permissions", tags=["permissions"]
)