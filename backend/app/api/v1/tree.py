from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import (
    ExceptionDetails,
    NotAllowedError,
    NotFoundError,
    PermissionDenniedError,
    TreeCreationError,
    TreeUpdatingError,
)
from app.core.permissions import (
    IsCurator,
    IsSectorCuratorOrCorrectTeam,
    IsTreeCuratorOrCorrectTeam,
    IsVolunteer,
    permission_dependency,
)
from app.core.user import current_user
from app.models import Sector, Tree, User
from app.repositories import SectorRepository, TreeRepository
from app.schemas import TreeCreate, TreeCreateWithAuthor, TreeRead, TreeUpdate
from app.services.tree_service import TreeService


async def get_sector_with_permissions(
    tree_in: TreeCreate,
    user: User = Depends(current_user),
    sector_repo: SectorRepository = Depends(),
) -> Sector:

    sector = await sector_repo.get(id=tree_in.sector_id)
    if not sector:
        raise NotFoundError(
            ExceptionDetails.get_not_found_detail(
                model_name=SectorRepository.model.verbose_name(),
                id=tree_in.sector_id,
            )
        )
    permission = await IsSectorCuratorOrCorrectTeam().has_obj_permission(
        user=user, obj=sector
    )
    if not permission:
        raise PermissionDenniedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)
    return sector


async def get_tree_with_permissions(
    tree_id: int,
    user: User = Depends(current_user),
    tree_repo: TreeRepository = Depends(),
) -> Tree:

    tree = await tree_repo.get(id=tree_id)
    if not tree:
        raise NotFoundError(
            ExceptionDetails.get_not_found_detail(
                model_name=TreeRepository.model.verbose_name(),
                id=tree_id,
            )
        )
    permission = await IsTreeCuratorOrCorrectTeam().has_obj_permission(
        user=user, obj=tree
    )
    if not permission:
        raise PermissionDenniedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)
    return tree


router = APIRouter()


@router.get(
    path="/trees",
    response_model=list[TreeRead],
    summary="Получение списка растений",
    description="Показывает список всех растений (деревьев) зарегистрированных \
        в приложении.",
)
async def get_all_trees(
    service: TreeService = Depends(),
) -> list[TreeRead]:
    trees_db = await service.get_all_trees()
    return [TreeRead.model_validate(obj=tree_db) for tree_db in trees_db]


@router.get(
    path="/trees/{tree_id}",
    response_model=TreeRead,
    status_code=status.HTTP_200_OK,
    summary="Получение растения",
    description="Показывает растение (дерево) по идентификатору (id).",
)
async def get_tree(tree_id: int, service: TreeService = Depends()) -> TreeRead:
    try:
        tree_db = await service.get_tree(obj_id=tree_id)
        return TreeRead.model_validate(obj=tree_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.get(
    path="/sectors/{sector_id}/trees",
    response_model=list[TreeRead],
    status_code=status.HTTP_200_OK,
    summary="Получение всех растений на участке",
    description="Показывает список всех растений (деревьев) на учетном участке\
        с определенным идентификатором (id).",
)
async def get_trees_by_sector_id(
    sector_id: int, service: TreeService = Depends()
) -> list[TreeRead]:
    trees_db = await service.get_trees_by_sector_id(sector_id=sector_id)
    return [TreeRead.model_validate(obj=tree_db) for tree_db in trees_db]


@router.post(
    path="/trees",
    response_model=TreeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового растения",
    description="Создает новое растение (дерево).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsVolunteer))
    ],
)
async def create_tree(
    tree_in: TreeCreate,
    current_user: User = Depends(dependency=current_user),
    sector: Sector = Depends(get_sector_with_permissions),
    service: TreeService = Depends(),
) -> TreeRead:
    try:
        tree_with_author = TreeCreateWithAuthor(
            **tree_in.model_dump(), author_id=current_user.id
        )

        tree_db = await service.create_tree(
            obj_in=tree_with_author, sector=sector
        )
        return TreeRead.model_validate(obj=tree_db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        ) from e
    except TreeCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.patch(
    path="/trees/{tree_id}",
    response_model=TreeRead,
    summary="Изменение растения",
    description="Изменяет поля записи растения по идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsCurator))
    ],
)
async def update_tree(
    tree_id: int,
    tree_in: TreeUpdate,
    tree_db: Tree = Depends(get_tree_with_permissions),
    service: TreeService = Depends(),
) -> TreeRead:
    try:
        tree_update_db = await service.update_tree(
            obj_in=tree_in, tree_db=tree_db
        )
        return TreeRead.model_validate(obj=tree_update_db)
    except TreeUpdatingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.delete(
    path="/trees/{tree_id}",
    description="Нельзя удалять зарегистрированные растения. Измените статус \
        растения на `Растение удалено`",
    deprecated=True,
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsCurator))
    ],
)
async def delete_tree(tree_id: int, service: TreeService = Depends()) -> None:
    try:
        await service.delete_tree(tree_id=tree_id)
    except NotAllowedError as e:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=str(e)
        ) from e
