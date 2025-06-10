from app.api.endpoints import user_router
from fastapi import APIRouter

main_router = APIRouter()

main_router.include_router(user_router)
