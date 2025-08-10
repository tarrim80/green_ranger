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
from app.models import Tree, User
from app.repositories.sector import SectorRepository
from app.repositories.tree import TreeRepository
from app.schemas import RoleEnum, TreeCreateWithAuthor, TreeUpdate
from app.services.mixins import CreateObjMixin, UpdateObjMixin


class TreeService(CreateObjMixin, UpdateObjMixin):
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
        location = obj_in.location.model_dump()
        await self._validate_location_in_sector(
            location=location, sector=sector
        )
        try:
            tree = await self.create_obj(obj_in=obj_in)
            return tree
        except Exception as e:
            raise TreeCreationError(
                ExceptionDetails.FAILED_CREATE_RECORD
            ) from e

    async def update_tree(
        self, obj_id: int, obj_in: TreeUpdate, user: User
    ) -> Tree:
        """Обновляет данные существующего растения с проверкой прав доступа."""
        try:
            tree_db: Tree = await self.repo.get(id=obj_id)
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
            if (
                location := obj_in.model_dump().get("location", None)
                is not None
            ):
                await self._validate_location_in_sector(
                    location=location, sector=tree_db.sector
                )
            tree_update = await self.update_obj(db_obj=tree_db, obj_in=obj_in)
            return tree_update
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

    async def _validate_location_in_sector(self, location, sector) -> None:
        """
        Проверяет что местоположение растения входит в обозначенный участок.
        """
        shapely_point = shape(context=location)
        wkt_point = WKTElement(
            data=shapely_point.wkt, srid=SRID_MERCATOR_WGS84
        )
        stmt = select(ST_Contains(sector.geometry, wkt_point))
        result = await self.repo.session.execute(stmt)
        is_contained = result.scalar.one()
        if not is_contained:
            raise ValueError(ExceptionDetails.TREE_LOCATION_OUTSIDE_OF_SECTOR)
