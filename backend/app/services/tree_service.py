from fastapi import Depends
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Contains
from shapely.geometry import shape
from sqlalchemy import select

from app.core.constants import SRID_MERCATOR_WGS84
from app.core.exceptions import (
    ExceptionDetails,
    NotAllowedError,
    NotFoundError,
    PermissionDenniedError,
    TreeCreationError,
    TreeUpdatingError,
)
from app.core.permissions import (
    IsSectorCuratorOrCorrectTeam,
    IsTreeCuratorOrCorrectTeam,
)
from app.core.transaction_manager import atomic_transaction
from app.models import Tree, User
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
        self, obj_in: TreeCreateWithAuthor, user: User
    ) -> Tree:
        """Создает новое растение."""
        sector = await self.sector_repo.get(id=obj_in.sector_id)
        if not sector:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.sector_repo.model.verbose_name(),
                    id=obj_in.sector_id,
                )
            )
        permission = await IsSectorCuratorOrCorrectTeam().has_obj_permission(
            user=user, obj=sector
        )
        if not permission:
            raise PermissionDenniedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)
        tree_data = obj_in.model_dump()
        if "location" in tree_data and isinstance(tree_data["location"], dict):
            shapely_point = shape(tree_data["location"])
            tree_data["location"] = WKTElement(
                shapely_point.wkt, srid=SRID_MERCATOR_WGS84
            )
            await self._validate_location_in_sector(
                wkt_location=tree_data["location"], sector=sector
            )
        try:
            async with atomic_transaction(session=self.repo.session):
                new_tree = self.repo.model(**tree_data)
                self.repo.session.add(instance=new_tree)
                await self.repo.session.flush()
            return new_tree
        except Exception as e:
            raise TreeCreationError(
                ExceptionDetails.FAILED_CREATE_RECORD
            ) from e

    async def update_tree(
        self, obj_id: int, obj_in: TreeUpdate, user: User
    ) -> Tree:
        """Обновляет данные существующего растения с проверкой прав доступа."""
        try:
            tree_db = await self.repo.get(id=obj_id)
            if not tree_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(),
                        id=obj_id,
                    )
                )
            permission = await IsTreeCuratorOrCorrectTeam().has_obj_permission(
                user=user, obj=tree_db
            )
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )
            update_data = obj_in.model_dump(exclude_unset=True)
            if location := update_data.get("location", None):
                shapely_point = shape(location)
                wkt_location = WKTElement(
                    shapely_point.wkt, srid=SRID_MERCATOR_WGS84
                )
                await self._validate_location_in_sector(
                    wkt_location=wkt_location, sector=tree_db.sector
                )
                update_data["location"] = wkt_location
            async with atomic_transaction(session=self.repo.session):
                for field, value in update_data.items():
                    setattr(tree_db, field, value)
                self.repo.session.add(instance=tree_db)
                await self.repo.session.flush()
                await self.repo.session.refresh(instance=tree_db)
            return tree_db
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

    async def _validate_location_in_sector(self, wkt_location, sector) -> None:
        """
        Проверяет что местоположение растения входит в обозначенный участок.
        """
        stmt = select(ST_Contains(sector.geometry, wkt_location))
        result = await self.repo.session.execute(stmt)
        is_contained = result.scalar()
        if not is_contained:
            raise ValueError(ExceptionDetails.TREE_LOCATION_OUTSIDE_OF_SECTOR)
