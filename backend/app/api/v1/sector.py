from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.api.v1.dependencies import (
    check_sector_modification_access,
    get_sector_db,
)
from app.core.exceptions import (
    SectorCreationError,
)
from app.core.permissions import (
    IsAdmin,
    IsCurator,
    permission_dependency,
)
from app.core.user import current_user
from app.models import Sector, User
from app.schemas import RoleEnum, SectorCreate, SectorRead, SectorUpdate
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
    sector_db: Sector = Depends(dependency=get_sector_db),
) -> SectorRead:
    return SectorRead.model_validate(obj=sector_db)


@router.post(
    path="/",
    response_model=SectorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового участка",
    description="Создает новый учетный участок в системе.",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsCurator))
    ],
)
async def create_sector(
    sector_in: SectorCreate,
    service: SectorService = Depends(),
    current_user: User = Depends(current_user),
) -> SectorRead:
    try:
        if current_user.role == RoleEnum.CURATOR:
            curator_id = current_user.id
            sector_db = await service.create_sector(
                sector_in=sector_in, curator_id=curator_id
            )
        else:
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
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsCurator)),
        Depends(dependency=check_sector_modification_access),
    ],
)
async def update_sector(
    sector_in: SectorUpdate,
    service: SectorService = Depends(),
    sector_db: Sector = Depends(dependency=get_sector_db),
) -> SectorRead:
    sector_update_db = await service.update_sector(
        sector_db=sector_db, obj_in=sector_in
    )
    return SectorRead.model_validate(obj=sector_update_db)


@router.delete(
    path="/{sector_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление учетного участка",
    description="Удаляет участок по его идентификатору (id)./n\
        Невозможно удалить участок, на котором зарегистрированны \
            растения./nНевозможно удалить участок, к которому прикреплена \
                команда волонтеров",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsAdmin)),
        Depends(dependency=check_sector_modification_access),
    ],
)
async def delete_sector(
    sector_db: Sector = Depends(dependency=get_sector_db),
    service: SectorService = Depends(),
) -> None:
    await service.delete_sector(sector=sector_db)
