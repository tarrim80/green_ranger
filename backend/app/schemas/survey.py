from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.defaults import SurveyDefaults
from app.schemas.enums import SurveyStatusEnum, TreeConditionEnum
from app.schemas.photo import PhotoRead
from app.schemas.user import UserShortRead

if TYPE_CHECKING:
    from app.schemas.survey_defect import SurveyDefectRead

SURVEY_FIELDS_CONFIG = {
    "id": Field(description="Уникальный идентификатор", examples=[1, 2, 3]),
    "age": Field(
        description="Возраст растения",
        examples=[24, 5],
        gt=0,
    ),
    "height": Field(
        description="Высота дерева в метрах",
        examples=[5.3],
        gt=0,
    ),
    "diameter": Field(
        description="Диаметр ствола, в см (на высоте 1,3 м, примерно \
            на высоте плеча)",
        examples=[36],
        gt=0,
    ),
    "trunk_count": Field(description="Количество стволов", examples=[1], gt=0),
    "condition": Field(
        description="КСО - Коэффициент состояния объекта (поле выбора)",
        examples=["Угнетенное"],
    ),
    "is_emergency_report": Field(
        description="Потенциально опасное",
        examples=[False, True],
    ),
    "note": Field(
        description="Общее примечание к обследованию",
        examples=["Повторное обследование для фиксации динамики"],
    ),
    "tree_id": Field(
        description="Идентификатор (ID) растения",
        examples=[8],
    ),
    "survey_status": Field(
        description="Статус обследования (поле выбора)",
        examples=["Одобрено"],
    ),
    "author_id": Field(
        description="ID пользователя выполняющего обследование",
        examples=[9],
    ),
    "author": Field(
        description="Волонтер выполняющий обследование",
        examples=["Иван Петров"],
    ),
    "survey_defects": Field(
        description="Список зафиксированных дефектов",
    ),
    "tree_photos": Field(description="Список фотографий общего вида растения"),
    "created_at": Field(description="Дата и время проведения обследования"),
    "updated_at": Field(description="Дата и время изменения данных"),
}


class SurveyBase(BaseModel):
    """Базовая схема для обследования."""

    age: Annotated[int | None, SURVEY_FIELDS_CONFIG["age"]] = None
    height: Annotated[float | None, SURVEY_FIELDS_CONFIG["height"]] = None
    diameter: Annotated[float | None, SURVEY_FIELDS_CONFIG["diameter"]] = None
    trunk_count: Annotated[int, SURVEY_FIELDS_CONFIG["trunk_count"]] = (
        SurveyDefaults.TRUNK_COUNT
    )
    condition: Annotated[
        TreeConditionEnum, SURVEY_FIELDS_CONFIG["condition"]
    ] = SurveyDefaults.CONDITION
    is_emergency_report: Annotated[
        bool, SURVEY_FIELDS_CONFIG["is_emergency_report"]
    ] = SurveyDefaults.IS_EMERGENCY_REPORT
    note: Annotated[str | None, SURVEY_FIELDS_CONFIG["note"]] = None


class SurveyCreate(SurveyBase):
    """Схема для создания обследования."""

    tree_id: Annotated[int, SURVEY_FIELDS_CONFIG["tree_id"]]
    author_id: Annotated[int, SURVEY_FIELDS_CONFIG["author_id"]]
    survey_status: Annotated[
        SurveyStatusEnum | None, SURVEY_FIELDS_CONFIG["survey_status"]
    ] = SurveyDefaults.SURVEY_STATUS


class SurveyUpdate(BaseModel):
    """Схема для обновления обследования."""

    # TODO: Подумать -- нужно ли давать возможность изменять tree_id
    tree_id: Annotated[int | None, SURVEY_FIELDS_CONFIG["tree_id"]] = None
    age: Annotated[int | None, SURVEY_FIELDS_CONFIG["age"]] = None
    height: Annotated[float | None, SURVEY_FIELDS_CONFIG["height"]] = None
    diameter: Annotated[float | None, SURVEY_FIELDS_CONFIG["diameter"]] = None
    trunk_count: Annotated[int | None, SURVEY_FIELDS_CONFIG["trunk_count"]] = (
        None
    )
    condition: Annotated[
        TreeConditionEnum | None, SURVEY_FIELDS_CONFIG["condition"]
    ] = None
    is_emergency_report: Annotated[
        bool | None, SURVEY_FIELDS_CONFIG["is_emergency_report"]
    ] = None
    note: Annotated[str | None, SURVEY_FIELDS_CONFIG["note"]] = None
    survey_status: Annotated[
        SurveyStatusEnum | None, SURVEY_FIELDS_CONFIG["survey_status"]
    ] = None


class SurveyShortRead(SurveyBase):
    """Схема для краткого представления обследования."""

    id: Annotated[int, SURVEY_FIELDS_CONFIG["id"]]
    tree_id: Annotated[int, SURVEY_FIELDS_CONFIG["tree_id"]]
    survey_status: Annotated[
        SurveyStatusEnum, SURVEY_FIELDS_CONFIG["survey_status"]
    ]
    author: Annotated[UserShortRead, SURVEY_FIELDS_CONFIG["author"]]

    model_config = ConfigDict(from_attributes=True)


class SurveyRead(SurveyShortRead):
    """Схема для чтения обследования со связанными сущностями."""

    created_at: Annotated[datetime, SURVEY_FIELDS_CONFIG["created_at"]]
    updated_at: Annotated[datetime, SURVEY_FIELDS_CONFIG["updated_at"]]
    tree_photos: Annotated[
        list[PhotoRead], SURVEY_FIELDS_CONFIG["tree_photos"]
    ]
    survey_defects: Annotated[
        list["SurveyDefectRead"], SURVEY_FIELDS_CONFIG["survey_defects"]
    ]
