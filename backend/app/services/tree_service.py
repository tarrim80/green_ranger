from operator import attrgetter

from fastapi import Depends
from geoalchemy2.elements import WKTElement
from shapely.geometry import shape

from app.core.constants import SRID_MERCATOR_WGS84
from app.core.exceptions import (
    ExceptionDetails,
    NotAllowedError,
    TreeCreationError,
    TreeUpdatingError,
)
from app.core.transaction_manager import atomic_transaction
from app.models import Sector, Survey, Tree
from app.repositories.sector import SectorRepository
from app.repositories.tree import TreeRepository
from app.schemas import SurveyStatusEnum, TreeCreateWithAuthor, TreeUpdate


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
            is_contained = await self.repo.check_location_in_sector(
                wkt_location=tree_data["location"], sector=sector
            )
            if not is_contained:
                raise ValueError(
                    ExceptionDetails.TREE_LOCATION_OUTSIDE_OF_SECTOR
                )

        try:
            async with atomic_transaction(session=self.repo.session):
                new_tree = self.repo.model(**tree_data)
                self.repo.session.add(instance=new_tree)
                await self.repo.session.flush()
        except Exception as e:
            raise TreeCreationError(
                f"{ExceptionDetails.FAILED_CREATE_RECORD}: {e}"
            )
        tree = await self.repo.get(id=new_tree.id)
        if not tree:
            raise TreeCreationError(ExceptionDetails.FAILED_CREATE_RECORD)
        return tree

    async def update_tree(self, obj_in: TreeUpdate, tree_db: Tree) -> Tree:
        """Обновляет данные существующего растения."""
        update_data = obj_in.model_dump(exclude_unset=True)
        if location := update_data.get("location", None):
            shapely_point = shape(location)
            wkt_location = WKTElement(
                shapely_point.wkt, srid=SRID_MERCATOR_WGS84
            )
            is_contained = await self.repo.check_location_in_sector(
                wkt_location=wkt_location, sector=tree_db.sector
            )
            if not is_contained:
                raise ValueError(
                    ExceptionDetails.TREE_LOCATION_OUTSIDE_OF_SECTOR
                )
            update_data["location"] = wkt_location

        try:
            async with atomic_transaction(session=self.repo.session):
                for field, value in update_data.items():
                    setattr(tree_db, field, value)
                self.repo.session.add(instance=tree_db)
                await self.repo.session.flush()
        except Exception as e:
            raise TreeUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            )
        tree = await self.repo.get(id=tree_db.id)
        if not tree:
            raise TreeUpdatingError(ExceptionDetails.FAILED_UPDATE_RECORD)
        return tree

    async def sync_state_tree_with_last_survey(
        self, tree: Tree, survey: Survey
    ) -> None:
        """
        Синхронизирует состояние растения
        с последним проведённым обследованием.
        """
        if survey.survey_status != SurveyStatusEnum.APPROVED:
            return
        actual_survey = max(tree.surveys, key=attrgetter("created_at"))
        if actual_survey.id != survey.id:
            return
        if all(
            [
                tree.condition == survey.condition,
                tree.is_emergency == survey.is_emergency_report,
            ]
        ):
            return

        tree.condition = survey.condition
        tree.is_emergency = survey.is_emergency_report
        return

    async def delete_tree(self, tree_id: int) -> None:
        """Запрещает прямое удаление растения."""
        raise NotAllowedError(ExceptionDetails.NOT_ALLOWED_REMOVE_TREES)
