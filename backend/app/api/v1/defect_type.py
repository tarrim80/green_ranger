from fastapi import Depends, File, Form, HTTPException, UploadFile, status
from fastapi.routing import APIRouter

from app.core.constants import ExceptionDetails
from app.core.exceptions import DefectTypeCreationError
from app.repositories import DefectTypeRepository
from app.schemas import DefectTypeRead, DefectTypeUpdate
from app.services.defect_type_service import DefectTypeService

router = APIRouter()


@router.get(
    path="/",
    response_model=list[DefectTypeRead],
    summary="Получение списка видов дефектов",
    description="Показывает список всех возможных видов дефектов.",
)
async def get_all_defect_types(
    repo: DefectTypeRepository = Depends(),
) -> list[DefectTypeRead]:
    db_defect_types = await repo.get_multi()
    return [
        DefectTypeRead.model_validate(obj=defect_type)
        for defect_type in db_defect_types
    ]


@router.get(
    path="/{defect_type_id}",
    response_model=DefectTypeRead,
    summary="Получение вида дефекта",
    description="Показывает вид дефекта по идентификатору (id).",
)
async def get_defect_type(
    defect_type_id: int, repo: DefectTypeRepository = Depends()
) -> DefectTypeRead:
    defect_type_db = await repo.get(id=defect_type_id)
    if not defect_type_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(
                model_name="Вид дефекта"
            ),
        )
    return DefectTypeRead.model_validate(obj=defect_type_db)


@router.post(
    path="/",
    response_model=DefectTypeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового вида дефекта",
    description="Создает новый вид дефекта в справочнике.",
)
async def create_defect_type(
    name: str = Form(default=...),
    description: str | None = Form(default=None),
    files: list[UploadFile] = File(default=...),
    service: DefectTypeService = Depends(),
) -> DefectTypeRead:
    try:
        defect_type_db = await service.create_with_photos(
            name=name, description=description, files=files
        )
        return DefectTypeRead.model_validate(obj=defect_type_db)
    except DefectTypeCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    path="/{defect_type_id}",
    response_model=DefectTypeRead,
    summary="Изменение вида дефекта",
    description="Изменяет поля записи вида дефекта по идентификатору (id).",
)
async def update_defect_type(
    defect_type_id: int,
    defect_type_in: DefectTypeUpdate,
    repo: DefectTypeRepository = Depends(),
) -> DefectTypeRead:
    defect_type_db = await repo.get(id=defect_type_id)
    if not defect_type_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(
                model_name="Вид дефекта"
            ),
        )
    defect_type_update_db = await repo.update(
        db_obj=defect_type_db, obj_in=defect_type_in
    )
    return DefectTypeRead.model_validate(obj=defect_type_update_db)


@router.delete(
    path="/{defect_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление вида дефекта",
    description="Удаляет вид дефекта по идентификатору (id).",
)
async def delete_defect_type(
    defect_type_id: int, service: DefectTypeService = Depends()
) -> None:
    if not await service.delete_with_photos(defect_type_id=defect_type_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(
                model_name="Вид дефекта"
            ),
        )
