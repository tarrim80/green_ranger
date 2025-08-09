from fastapi import Depends
from geoalchemy2.elements import WKTElement
from shapely.geometry import shape
from sqlalchemy.exc import IntegrityError

from app.core.constants import SRID_MERCATOR_WGS84
from app.core.exceptions import (
    ExceptionDetails,
    NotAllowedError,
    NotFoundError,
    SectorCreationError,
    SectorRemovingError,
    SectorUpdatingError,
)
from app.core.transaction_manager import atomic_transaction
from app.models import Sector, User
from app.repositories.sector import SectorRepository
from app.schemas import RoleEnum, SectorCreate, SectorUpdate
from app.services.mixins import DeleteObjMixin


class SectorService(DeleteObjMixin):
    """Сервисный слой для управления учетными участками."""

    def __init__(
        self,
        repo: SectorRepository = Depends(),
    ) -> None:
        self.repo = repo

    async def get_all_sectors(
        self,
    ) -> list[Sector]:
        """Получает список всех учетных участков."""
        sectors_db = await self.repo.get_multi()
        return list(sectors_db)

    async def get_sector(self, obj_id: int) -> Sector:
        """Получает учетный участок по его идентификатору."""
        sector_db = await self.repo.get(id=obj_id)
        if not sector_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.repo.model.verbose_name(),
                    id=obj_id,
                )
            )
        return sector_db

    async def create_sector(
        self, sector_in: SectorCreate, user: User
    ) -> Sector:
        """Создает новый учетный участок."""
        shapely_geom = shape(context=sector_in.geometry)
        wkt_element = WKTElement(
            data=shapely_geom.wkt, srid=SRID_MERCATOR_WGS84
        )
        sector_data = sector_in.model_dump()
        sector_data["geometry"] = wkt_element
        if user.role == RoleEnum.CURATOR:
            sector_data["curator_id"] = user.id
        try:
            async with atomic_transaction(session=self.repo.session):
                new_sector = self.repo.model(**sector_data)
                self.repo.session.add(instance=new_sector)
                await self.repo.session.flush()
            new_sector_id = new_sector.id
            fully_loaded_sector = await self.repo.get(id=new_sector_id)
            if not fully_loaded_sector:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name,
                        id=new_sector_id,
                    )
                )
            return fully_loaded_sector
        except IntegrityError as e:
            raise SectorCreationError(
                ExceptionDetails.ALREADY_EXIST_SECTOR_NAME
            ) from e
        except Exception as e:
            raise SectorCreationError(
                f"{ExceptionDetails.FAILED_CREATE_RECORD}: {e}"
            ) from e

    async def update_sector(
        self, obj_id: int, obj_in: SectorUpdate, user: User
    ) -> Sector:
        """Обновляет данные существующего учетного участка."""
        try:
            sector_db: Sector = await self.repo.get(id=obj_id)
            if not sector_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(),
                        id=obj_id,
                    )
                )
            update_data = obj_in.model_dump()
            if geometry_dict := update_data.get("geometry", None):
                shapely_geom = shape(context=geometry_dict)
                wkt_element = WKTElement(
                    data=shapely_geom.wkt, srid=SRID_MERCATOR_WGS84
                )
                update_data["geometry"] = wkt_element
            if user.role == RoleEnum.CURATOR:
                curator_id = (
                    update_data.get("curator_id", None) or sector_db.curator_id
                )
                if curator_id != user.id:
                    raise NotAllowedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)
            async with atomic_transaction(session=self.repo.session):
                for field, value in update_data.items():
                    setattr(sector_db, field, value)

                self.repo.session.add(instance=sector_db)
                await self.repo.session.flush()
                await self.repo.session.refresh(instance=sector_db)
            return sector_db
        except (NotFoundError, NotAllowedError):
            raise
        except Exception as e:
            raise SectorUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            ) from e

    async def delete_sector(self, sector_id: int) -> None:
        """Удаляет учетный участок с проверкой связанных сущностей."""
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
