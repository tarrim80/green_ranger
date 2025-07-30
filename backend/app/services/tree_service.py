from fastapi import Depends

from app.core.exceptions import (
    ExceptionDetails,
    NotAllowedError,
    NotFoundError,
    PermissionDenniedError,
    TreeCreationError,
    TreeUpdatingError,
)
from app.core.permissions import IsTreeCuratorOrCorrectTeam
from app.models import Tree, User
from app.repositories.tree import TreeRepository
from app.schemas import TreeCreateWithAuthor, TreeUpdate
from app.services.mixins import CreateObjMixin, UpdateObjMixin


class TreeService(CreateObjMixin, UpdateObjMixin):
    def __init__(self, repo: TreeRepository = Depends()) -> None:
        self.repo = repo

    async def get_all_trees(self) -> list[Tree]:
        trees_db = await self.repo.get_multi()
        return list(trees_db)

    async def get_tree(self, obj_id: int) -> Tree:
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
        trees_db = await self.repo.get_all_by_sector_id(sector_id=sector_id)
        return list(trees_db)

    # TODO: Ограничить доступ на создание растения только в границах учетного
    #       участка и только пользователями, относящимися к участку
    #       (команда волонтеров или куратор).

    async def create_tree(self, obj_in: TreeCreateWithAuthor) -> Tree:
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
                    ExceptionDetails.NO_RIGHNT_FOR_ACTION
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
        raise NotAllowedError(ExceptionDetails.NOT_ALLOWED_REMOVE_TREES)
