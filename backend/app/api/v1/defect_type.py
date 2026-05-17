from fastapi import Depends, File, Form, UploadFile, status
from fastapi.routing import APIRouter

from app.api.v1.dependencies import get_defect_type_db
from app.core.permissions import IsAdmin, permission_dependency
from app.models.defect_type import DefectType
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
    service: DefectTypeService = Depends(),
) -> list[DefectTypeRead]:
    defect_types_db = await service.get_all_defect_types()
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
    defect_type_db: DefectType = Depends(get_defect_type_db),
) -> DefectTypeRead:
    return DefectTypeRead.model_validate(obj=defect_type_db)


@router.post(
    path="/",
    response_model=DefectTypeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового вида дефекта",
    description="Создает новый вид дефекта в справочнике.",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsAdmin))
    ],
)
async def create_defect_type(
    name: str = Form(default=...),
    description: str | None = Form(default=None),
    files: list[UploadFile] | None = File(default=None),
    service: DefectTypeService = Depends(),
) -> DefectTypeRead:
    defect_type_in = DefectTypeCreate(
        name=name,
        description=description,
    )
    defect_type_db = await service.create_with_photos(
        defect_type_in=defect_type_in, files=files
    )
    return DefectTypeRead.model_validate(obj=defect_type_db)


@router.post(
    path="/{defect_type_id}/images",
    response_model=list[PhotoRead],
    status_code=status.HTTP_201_CREATED,
    summary="Добавление изображений к виду дефекта",
    description="Загружает одно или несколько изображений \
        и привязывает их к существующему виду дефекта.",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsAdmin))
    ],
)
async def add_images_to_defect_type(
    defect_type_id: int,
    files: list[UploadFile],
    service: PhotoService = Depends(),
) -> list[PhotoRead]:
    images = await service.upload_and_link_photos(
        files=files,
        defect_type_id=defect_type_id,
    )
    return [PhotoRead.model_validate(image) for image in images]


@router.patch(
    path="/{defect_type_id}",
    response_model=DefectTypeRead,
    summary="Изменение вида дефекта",
    description="Изменяет поля записи вида дефекта по идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsAdmin))
    ],
)
async def update_defect_type(
    defect_type_in: DefectTypeUpdate,
    defect_type_db: DefectType = Depends(get_defect_type_db),
    service: DefectTypeService = Depends(),
) -> DefectTypeRead:
    defect_type_update_db = await service.update_defect_type(
        defect_type_db=defect_type_db, obj_in=defect_type_in
    )
    return DefectTypeRead.model_validate(obj=defect_type_update_db)


@router.delete(
    path="/{defect_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление вида дефекта",
    description="Удаляет вид дефекта по идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsAdmin))
    ],
)
async def delete_defect_type(
    defect_type_db: DefectType = Depends(get_defect_type_db),
    service: DefectTypeService = Depends(),
) -> None:
    await service.delete_with_images(defect_type_db=defect_type_db)
