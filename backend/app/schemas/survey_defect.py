from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import SurveyDefectDefaults
from app.schemas import (
    DefectStatusEnum,
    DefectTypeShortRead,
    PhotoRead,
    SurveyShortRead,
)

SURVEY_DEFECT_FIELDS_CONFIG = {
    "id": Field(description="Уникальный идентификатор", examples=[1, 2, 3]),
    "survey_id": Field(
        description="Идентификатор (ID) обследования, в ходе которого \
            обнаружен данный дефект",
        examples=[1, 2, 3],
    ),
    "survey": Field(
        description="Обследование, в ходе которого \
            обнаружен данный дефект",
        examples=[SurveyShortRead],
    ),
    "defect_type_id": Field(
        description="Идентификатор (ID) вида дефекта",
        examples=[1, 2, 3],
    ),
    "description": Field(
        description="Описание обнаруженного дефекта",
        examples=[
            "Сухие участки корневой системы на поверхности",
        ],
    ),
    "defect_status": Field(
        description="Текущий статус дефекта (поле выбора)",
        examples=[
            "В работе",
        ],
    ),
    "photos": Field(description="Список фотографий дефекта"),
    "defect_type": Field(
        description="Вид дефекта",
        examples=[
            "Трещина",
        ],
    ),
}


class SurveyDefectBase(BaseModel):
    survey_id: Annotated[int, SURVEY_DEFECT_FIELDS_CONFIG["survey_id"]]
    defect_type_id: Annotated[
        int, SURVEY_DEFECT_FIELDS_CONFIG["defect_type_id"]
    ]
    description: Annotated[
        str | None, SURVEY_DEFECT_FIELDS_CONFIG["description"]
    ] = None
    defect_status: Annotated[
        DefectStatusEnum | None, SURVEY_DEFECT_FIELDS_CONFIG["defect_status"]
    ] = SurveyDefectDefaults.DEFECT_STATUS


class SurveyDefectCreate(SurveyDefectBase):
    pass


class SurveyDefectUpdate(BaseModel):
    description: Annotated[
        str | None, SURVEY_DEFECT_FIELDS_CONFIG["description"]
    ] = None
    defect_status: Annotated[
        DefectStatusEnum | None, SURVEY_DEFECT_FIELDS_CONFIG["defect_status"]
    ] = None


class SurveyDefectRead(BaseModel):
    id: Annotated[int, SURVEY_DEFECT_FIELDS_CONFIG["id"]]
    survey: Annotated[SurveyShortRead, SURVEY_DEFECT_FIELDS_CONFIG["survey"]]
    description: Annotated[
        str | None, SURVEY_DEFECT_FIELDS_CONFIG["description"]
    ]
    defect_status: Annotated[
        DefectStatusEnum, SURVEY_DEFECT_FIELDS_CONFIG["defect_status"]
    ]
    photos: Annotated[list[PhotoRead], SURVEY_DEFECT_FIELDS_CONFIG["photos"]]
    defect_type: Annotated[
        DefectTypeShortRead, SURVEY_DEFECT_FIELDS_CONFIG["defect_type"]
    ]

    model_config = ConfigDict(from_attributes=True)
