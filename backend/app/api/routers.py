from fastapi import APIRouter

from app.api.v1 import (
    defect_type_router,
    photo_router,
    role_router,
    survey_defect_router,
    survey_router,
    user_router,
)

main_router = APIRouter(prefix="/api/v1")

main_router.include_router(router=user_router)
main_router.include_router(router=role_router, prefix="/roles", tags=["Роли"])
main_router.include_router(
    router=defect_type_router,
    prefix="/defect-types",
    tags=["Виды дефектов (справочник)"],
)
main_router.include_router(
    router=photo_router, prefix="/photos", tags=["Фотографии / Изображения"]
)
main_router.include_router(
    router=survey_defect_router,
    tags=["Обнаруженные дефекты"],
)
main_router.include_router(
    router=survey_router, tags=["Обследования (Осмотры)"]
)
# main_router.include_router(router=team_router, prefix="/teams", tags=["Команды"])
# main_router.include_router(router=ticket_router, prefix="/tickets", tags=["Заявки"])
# main_router.include_router(
#     router=sector_router, prefix="/sectors", tags=["Учетные участки"]
# )
