from fastapi import Depends, File, Form, HTTPException, UploadFile, status
from fastapi.routing import APIRouter

from app.core.constants import ExceptionDetails
from app.core.exceptions import DefectTypeCreationError, PhotoCreationError
from app.repositories import DefectTypeRepository
from app.schemas import (
    DefectTypeCreate,
    DefectTypeRead,
    DefectTypeUpdate,
    PhotoRead,
)
from app.services.defect_type_service import DefectTypeService
from app.services.photo_service import PhotoService

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
    defect_types_db = await repo.get_multi()
    return [
        DefectTypeRead.model_validate(obj=defect_type_db)
        for defect_type_db in defect_types_db
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
    defect_type_in = DefectTypeCreate(
        name=name,
        description=description,
    )
    try:
        defect_type_db = await service.create_with_photos(
            defect_type_in=defect_type_in, files=files
        )
        return DefectTypeRead.model_validate(obj=defect_type_db)
    except DefectTypeCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    path="/{defect_type_id}/images",
    response_model=list[PhotoRead],
    status_code=status.HTTP_201_CREATED,
    summary="Добавление избражений к виду дефекта",
    description="Загружает одно или несколько изображений \
        и привязывает их к существующему виду дефекта.",
)
async def add_images_to_defect_type(
    defect_type_id: int,
    files: list[UploadFile],
    service: PhotoService = Depends(),
) -> list[PhotoRead]:
    try:
        images = await service.upload_and_link_photos(
            files=files,
            defect_type_id=defect_type_id,
        )
        return [PhotoRead.model_validate(image) for image in images]
    except PhotoCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ExceptionDetails.FAILED_CREATE_PHOTO} {e}",
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
