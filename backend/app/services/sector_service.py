from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from app.core.constants import ExceptionDetails
from app.core.exceptions import (
    NotAllowedError,
    NotFoundError,
    SectorCreationError,
    SectorRemovingError,
)
from app.core.transaction_manager import atomic_transaction
from app.models import Sector
from app.repositories.sector import SectorRepository
from app.schemas import SectorCreate


class SectorService:
    def __init__(
        self,
        repo: SectorRepository = Depends(),
    ) -> None:
        self.repo = repo

    async def create_sector(self, sector_in: SectorCreate) -> Sector:
        try:
            return await self.repo.create(obj_in=sector_in)
        except Exception as e:
            if isinstance(e, IntegrityError):
                raise SectorCreationError(
                    ExceptionDetails.ALREADY_EXIST_SECTOR_NAME
                )
            raise SectorCreationError(
                f"{ExceptionDetails.FAILED_CREATE_RECORD}: {e}"
            )

    async def delete_sector(self, sector_id: int) -> None:
        try:
            async with atomic_transaction(session=self.repo.session):
                sector = await self.repo.get(id=sector_id)
                if not sector:
                    raise NotFoundError(
                        ExceptionDetails.get_not_found_detail(
                            model_name="Учетный участок", id=sector_id
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
                sector = await self.repo.remove(id=sector_id)
        except NotFoundError as e:
            raise
        except NotAllowedError as e:
            raise
        except Exception as e:
            raise SectorRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_RECORD}: {e}"
            ) from e
