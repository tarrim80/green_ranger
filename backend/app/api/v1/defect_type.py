from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.core.constants import ExceptionDetails
from app.repositories import DefectTypeRepository
from app.schemas import DefectTypeCreate, DefectTypeRead, DefectTypeUpdate

router = APIRouter()


@router.get(
    path="/",
    response_model=list[DefectTypeRead],
    summary="Получение списка видов дефектов",
    description="Показывает список всех возможных видов дефектов.",
)
async def get_all_defect_types(
    repo: DefectTypeRepository = Depends(),
) -> list[DefectTypeRead]:
    db_defect_types = await repo.get_multi()
    return [
        DefectTypeRead.model_validate(obj=defect_type)
        for defect_type in db_defect_types
    ]


@router.get(
    path="/{defect_type_id}",
    response_model=DefectTypeRead,
    summary="Получение вида дефекта",
    description="Показывает вид дефекта идентификатору (id).",
)
async def get_defect_type(
    defect_type_id: int, repo: DefectTypeRepository = Depends()
) -> DefectTypeRead:
    defect_type_db = await repo.get(id=defect_type_id)
    if not defect_type_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(
                model_name="Вид дефекта"
            ),
        )
    return DefectTypeRead.model_validate(obj=defect_type_db)


@router.post(
    path="/",
    response_model=DefectTypeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового вида дефекта",
    description="Создает новый вид дефекта в справочнике.",
)
async def create_defect_type(
    defect_type_in: DefectTypeCreate, repo: DefectTypeRepository = Depends()
) -> DefectTypeRead:
    defect_type_db = await repo.create(obj_in=defect_type_in)
    return DefectTypeRead.model_validate(obj=defect_type_db)


@router.patch(
    path="/{defect_type_id}",
    response_model=DefectTypeRead,
    summary="Изменение вида дефекта",
    description="Изменяет поля записи вида дефекта по идентификатору (id).",
)
async def defect_type_update(
    defect_type_id: int,
    defect_type_in: DefectTypeUpdate,
    repo: DefectTypeRepository = Depends(),
) -> DefectTypeRead:
    defect_type_db = await repo.get(id=defect_type_id)
    if not defect_type_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(
                model_name="Вид дефекта"
            ),
        )
    defect_type_update_db = await repo.update(
        db_obj=defect_type_db, obj_in=defect_type_in
    )
    return DefectTypeRead.model_validate(obj=defect_type_update_db)


@router.delete(
    path="/{defect_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление вида дефекта",
    description="Удаляет вид дефекта по идентификатору (id).",
)
async def defect_type_delete(
    defect_type_id: int, repo: DefectTypeRepository = Depends()
) -> None:
    if not await repo.remove(id=defect_type_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(
                model_name="Вид дефекта"
            ),
        )
