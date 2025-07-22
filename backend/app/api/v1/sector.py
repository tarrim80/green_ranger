from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.core.exceptions import (
    NotAllowedError,
    NotFoundError,
    SectorCreationError,
    SectorRemovingError,
    SectorUpdatingError,
)
from app.schemas import SectorCreate, SectorRead, SectorUpdate
from app.services.sector_service import SectorService

router = APIRouter()


@router.get(
    path="/",
    response_model=list[SectorRead],
    summary="Получение списка учетных участков",
    description="Показывает список всех зарегистрированных участков.",
)
async def get_all_sectors(
    service: SectorService = Depends(),
) -> list[SectorRead]:
    sectors_db = await service.get_all_sectors()
    return [
        SectorRead.model_validate(obj=sector_db) for sector_db in sectors_db
    ]


@router.get(
    path="/{sector_id}",
    response_model=SectorRead,
    summary="Получение учетного участка",
    description="Показывает участок по его идентификатору (id).",
)
async def get_sector(
    sector_id: int, service: SectorService = Depends()
) -> SectorRead:
    try:
        sector_db = await service.get_sector(obj_id=sector_id)
        return SectorRead.model_validate(obj=sector_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.post(
    path="/",
    response_model=SectorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового участка",
    description="Создает новый учетный участок в системе.",
)
async def create_sector(
    sector_in: SectorCreate, service: SectorService = Depends()
) -> SectorRead:
    try:
        sector_db = await service.create_sector(sector_in=sector_in)
        return SectorRead.model_validate(obj=sector_db)
    except SectorCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    path="/{sector_id}",
    response_model=SectorRead,
    summary="Изменение учетного участка",
    description="Изменяет поля записи в конкретном участке \
        по его идентификатору (id).",
)
async def update_sector(
    sector_id: int, sector_in: SectorUpdate, service: SectorService = Depends()
) -> SectorRead:
    try:
        sector_update_db = await service.update_sector(
            obj_id=sector_id, obj_in=sector_in
        )
        return SectorRead.model_validate(obj=sector_update_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except SectorUpdatingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.delete(
    path="/{sector_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление учетного участка",
    description="Удаляет участок по его идентификатору (id)./n\
        Невозможно удалить участок, на котором зарегистрированны \
            растения./nНевозможно удалить участок, к которому прикреплена \
                команда волонтеров",
)
async def delete_sector(
    sector_id: int, service: SectorService = Depends()
) -> None:
    try:
        await service.delete_sector(sector_id=sector_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except NotAllowedError as e:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=str(e),
        ) from e
    except SectorRemovingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
