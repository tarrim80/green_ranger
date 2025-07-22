from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    ExceptionDetails,
    NotAllowedError,
    NotFoundError,
    SectorCreationError,
    SectorRemovingError,
    SectorUpdatingError,
)
from app.core.transaction_manager import atomic_transaction
from app.models import Sector
from app.repositories.sector import SectorRepository
from app.schemas import SectorCreate, SectorUpdate
from app.services.mixins import DeleteObjMixin, UpdateObjMixin


class SectorService(UpdateObjMixin, DeleteObjMixin):
    def __init__(
        self,
        repo: SectorRepository = Depends(),
    ) -> None:
        self.repo = repo

    async def get_all_sectors(
        self,
    ) -> list[Sector]:
        sectors_db = await self.repo.get_multi()
        return list(sectors_db)

    async def get_sector(self, obj_id: int) -> Sector:
        sector_db = await self.repo.get(id=obj_id)
        if not sector_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.repo.model.verbose_name(),
                    id=obj_id,
                )
            )
        return sector_db

    async def create_sector(self, sector_in: SectorCreate) -> Sector:
        try:
            async with atomic_transaction(session=self.repo.session):
                new_sector = await self.repo.create(obj_in=sector_in)
                await self.repo.session.flush()
                await self.repo.session.refresh(instance=new_sector)
            return new_sector
        except Exception as e:
            if isinstance(e, IntegrityError):
                raise SectorCreationError(
                    ExceptionDetails.ALREADY_EXIST_SECTOR_NAME
                )
            raise SectorCreationError(
                f"{ExceptionDetails.FAILED_CREATE_RECORD}: {e}"
            )

    async def update_sector(self, obj_id: int, obj_in: SectorUpdate) -> Sector:
        try:
            sector_db = await self.repo.get(id=obj_id)
            if not sector_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(),
                        id=obj_id,
                    )
                )
            sector = await self.update_obj(db_obj=sector_db, obj_in=obj_in)
            return sector
        except NotFoundError:
            raise
        except Exception as e:
            raise SectorUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            ) from e

    async def delete_sector(self, sector_id: int) -> None:
        try:
            sector = await self.repo.get(id=sector_id)
            if not sector:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(),
                        id=sector_id,
                    )
                )
            if sector.team_id:
                raise NotAllowedError(
                    ExceptionDetails.NOT_ALLOWED_REMOVE_SECTOR_WITH_TEAM
                )
            if sector.trees:
                raise NotAllowedError(
                    ExceptionDetails.NOT_ALLOWED_REMOVE_SECTOR_WITH_TREES
                )
            await self.delete_obj(obj_id=sector_id)
        except NotFoundError as e:
            raise
        except NotAllowedError as e:
            raise
        except Exception as e:
            raise SectorRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_RECORD}: {e}"
            ) from e
