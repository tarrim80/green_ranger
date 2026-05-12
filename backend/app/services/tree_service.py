from fastapi import Depends
from geoalchemy2.elements import WKTElement
from shapely.geometry import shape

from app.core.constants import SRID_MERCATOR_WGS84
from app.core.exceptions import (
    ExceptionDetails,
    NotAllowedError,
    NotFoundError,
    PermissionDenniedError,
    TreeCreationError,
    TreeUpdatingError,
)
from app.core.transaction_manager import atomic_transaction
from app.models import Sector, Tree
from app.repositories.sector import SectorRepository
from app.repositories.tree import TreeRepository
from app.schemas import TreeCreateWithAuthor, TreeUpdate


class TreeService:
    """Сервисный слой для управления растениями (деревьями)."""

    def __init__(
        self,
        repo: TreeRepository = Depends(),
        sector_repo: SectorRepository = Depends(),
    ) -> None:
        self.repo = repo
        self.sector_repo = sector_repo

    async def get_all_trees(self) -> list[Tree]:
        """Получает список всех растений."""
        trees_db = await self.repo.get_multi()
        return list(trees_db)

    async def get_tree(self, obj_id: int) -> Tree:
        """Получает растение по его идентификатору."""
        tree_db = await self.repo.get(id=obj_id)
        if not tree_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.repo.model.verbose_name(),
                    id=obj_id,
                )
            )
        return tree_db

    async def get_trees_by_sector_id(self, sector_id: int) -> list[Tree]:
        """Получает все растения для конкретного учетного участка."""
        trees_db = await self.repo.get_all_by_sector_id(sector_id=sector_id)
        return list(trees_db)

    # TODO: Сделать автоматическое присвоение номера участка по координатам
    #       дерева

    async def create_tree(
        self, obj_in: TreeCreateWithAuthor, sector: Sector
    ) -> Tree:
        """Создает новое растение."""
        tree_data = obj_in.model_dump()
        if "location" in tree_data and isinstance(tree_data["location"], dict):
            shapely_point = shape(tree_data["location"])
            tree_data["location"] = WKTElement(
                shapely_point.wkt, srid=SRID_MERCATOR_WGS84
            )
            await self.repo.validate_location_in_sector(
                wkt_location=tree_data["location"], sector=sector
            )
        try:
            async with atomic_transaction(session=self.repo.session):
                new_tree = self.repo.model(**tree_data)
                self.repo.session.add(instance=new_tree)
                await self.repo.session.flush()
            return await self.get_tree(obj_id=new_tree.id)
        except Exception as e:
            raise TreeCreationError(
                ExceptionDetails.FAILED_CREATE_RECORD
            ) from e

    async def update_tree(self, obj_in: TreeUpdate, tree_db: Tree) -> Tree:
        """Обновляет данные существующего растения с проверкой прав доступа."""
        try:
            update_data = obj_in.model_dump(exclude_unset=True)
            if location := update_data.get("location", None):
                shapely_point = shape(location)
                wkt_location = WKTElement(
                    shapely_point.wkt, srid=SRID_MERCATOR_WGS84
                )
                await self.repo.validate_location_in_sector(
                    wkt_location=wkt_location, sector=tree_db.sector
                )
                update_data["location"] = wkt_location
            async with atomic_transaction(session=self.repo.session):
                for field, value in update_data.items():
                    setattr(tree_db, field, value)
                self.repo.session.add(instance=tree_db)
                await self.repo.session.flush()
            return await self.get_tree(obj_id=tree_db.id)
        except NotFoundError:
            raise
        except PermissionDenniedError:
            raise
        except Exception as e:
            raise TreeUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            ) from e

    async def delete_tree(self, tree_id: int) -> None:
        """Запрещает прямое удаление растения."""
        raise NotAllowedError(ExceptionDetails.NOT_ALLOWED_REMOVE_TREES)
