from fastapi import APIRouter

from app.api.v1 import role_router, user_router

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(router=user_router)
main_router.include_router(router=role_router, prefix="/roles", tags=["Роли"])
# main_router.include_router(router=team_router, prefix="/teams", tags=["Команды"])
# main_router.include_router(router=ticket_router, prefix="/tickets", tags=["Заявки"])
# main_router.include_router(
#     router=sector_router, prefix="/sectors", tags=["Учетные участки"]
# )
# main_router.include_router(
#     router=defect_router, prefix="/defects", tags=["Виды дефектов (справочник)"]
# )
