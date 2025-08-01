from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.photo import PhotoRead

DEFECT_TYPE_FIELDS_CONFIG = {
    "id": Field(description="Уникальный идентификатор", examples=[1, 2, 3]),
    "name": Field(
        description="Название вида дефекта растения",
        examples=["Некроз", "Трещина"],
    ),
    "description": Field(
        description="Описание вида дефекта",
        examples=[
            "Участок с поврежденной или отсутствующей корой",
            "Глубокий раскол ствола",
        ],
    ),
    "images": Field(description="Список изображений вида дефекта"),
}


class DefectTypeBase(BaseModel):
    """Базовая схема для вида дефекта."""

    name: Annotated[str, DEFECT_TYPE_FIELDS_CONFIG["name"]]
    description: Annotated[
        str | None, DEFECT_TYPE_FIELDS_CONFIG["description"]
    ] = None


class DefectTypeCreate(DefectTypeBase):
    """Схема для создания вида дефекта."""

    pass


class DefectTypeUpdate(BaseModel):
    """Схема для обновления вида дефекта."""

    name: Annotated[str | None, DEFECT_TYPE_FIELDS_CONFIG["name"]] = None
    description: Annotated[
        str | None, DEFECT_TYPE_FIELDS_CONFIG["description"]
    ] = None


class DefectTypeShortRead(BaseModel):
    """Схема для краткого представления вида дефекта."""

    id: Annotated[int, DEFECT_TYPE_FIELDS_CONFIG["id"]]
    name: Annotated[str, DEFECT_TYPE_FIELDS_CONFIG["name"]]

    model_config = ConfigDict(from_attributes=True)


class DefectTypeRead(DefectTypeBase):
    """Схема для чтения вида дефекта со связанными изображениями."""

    id: Annotated[int, DEFECT_TYPE_FIELDS_CONFIG["id"]]
    images: Annotated[list[PhotoRead], DEFECT_TYPE_FIELDS_CONFIG["images"]]

    model_config = ConfigDict(from_attributes=True)
