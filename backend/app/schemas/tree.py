from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from geojson_pydantic import Point
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.defaults import TreeDefaults

if TYPE_CHECKING:
    from app.schemas import SectorShortRead, TreeConditionEnum, UserShortRead

TREE_FIELDS_CONFIG = {
    "id": Field(description="Уникальный идентификатор", examples=[1, 2, 3]),
    "planting": Field(
        description="Вид насаждений", examples=["Одиночное", "Групповое"]
    ),
    "species": Field(
        description="Порода растения",
        examples=["Береза повислая", "Дуб черешчатый"],
    ),
    "description": Field(
        description="Описание растения",
        examples=["Дерево с раскидистой кроной у северного входа."],
    ),
    "location": Field(description="Местоположение растения (Point geometry)"),
    "azimuth": Field(
        description="Азимут от точки привязки до растения в градусах",
        examples=[180.5],
    ),
    "distance": Field(
        description="Расстояние от точки привязки до растения в метрах",
        examples=[15.2],
    ),
    "sector_id": Field(
        description="ID учетного участка, к которому привязано растение",
        examples=[1],
    ),
    "sector": Field(
        description="Учетный участок, к которому привязано растение"
    ),
    "condition": Field(description="КСО - Коэффициент состояния объекта"),
    "is_emergency": Field(
        description="Признак аварийности/срочности", examples=[False, True]
    ),
    "author_id": Field(
        description="ID автора, зарегистрировавшего растение", examples=[5]
    ),
    "author": Field(description="Автор, зарегистрировавший растение"),
    "created_at": Field(description="Дата и время создания записи"),
    "updated_at": Field(
        description="Дата и время последнего обновления записи"
    ),
}


class TreeBase(BaseModel):
    planting: Annotated[str, TREE_FIELDS_CONFIG["planting"]]
    species: Annotated[str, TREE_FIELDS_CONFIG["species"]]
    description: Annotated[str, TREE_FIELDS_CONFIG["description"]]
    location: Annotated[Point, TREE_FIELDS_CONFIG["location"]]
    azimuth: Annotated[float | None, TREE_FIELDS_CONFIG["azimuth"]] = None
    distance: Annotated[float | None, TREE_FIELDS_CONFIG["distance"]] = None
    condition: Annotated[
        "TreeConditionEnum", TREE_FIELDS_CONFIG["condition"]
    ] = TreeDefaults.CONDITION
    is_emergency: Annotated[bool, TREE_FIELDS_CONFIG["is_emergency"]] = (
        TreeDefaults.IS_EMERGENCY
    )


class TreeCreate(TreeBase):
    sector_id: Annotated[int, TREE_FIELDS_CONFIG["sector_id"]]


class TreeCreateWithAuthor(TreeCreate):
    author_id: Annotated[int, TREE_FIELDS_CONFIG["author_id"]]


class TreeUpdate(BaseModel):
    planting: Annotated[str | None, TREE_FIELDS_CONFIG["planting"]] = None
    species: Annotated[str | None, TREE_FIELDS_CONFIG["species"]] = None
    description: Annotated[str | None, TREE_FIELDS_CONFIG["description"]] = (
        None
    )
    location: Annotated[Point | None, TREE_FIELDS_CONFIG["location"]] = None
    azimuth: Annotated[float | None, TREE_FIELDS_CONFIG["azimuth"]] = None
    distance: Annotated[float | None, TREE_FIELDS_CONFIG["distance"]] = None
    sector_id: Annotated[int | None, TREE_FIELDS_CONFIG["sector_id"]] = None
    condition: Annotated[
        "TreeConditionEnum | None", TREE_FIELDS_CONFIG["condition"]
    ] = None
    is_emergency: Annotated[
        bool | None, TREE_FIELDS_CONFIG["is_emergency"]
    ] = None


class TreeRead(TreeBase):
    id: Annotated[int, TREE_FIELDS_CONFIG["id"]]
    sector: Annotated["SectorShortRead", TREE_FIELDS_CONFIG["sector"]]
    author: Annotated["UserShortRead", TREE_FIELDS_CONFIG["author"]]
    created_at: Annotated[datetime, TREE_FIELDS_CONFIG["created_at"]]
    updated_at: Annotated[datetime, TREE_FIELDS_CONFIG["updated_at"]]

    model_config = ConfigDict(from_attributes=True)


class TreeShortRead(BaseModel):
    id: Annotated[int, TREE_FIELDS_CONFIG["id"]]
    sector: Annotated["SectorShortRead", TREE_FIELDS_CONFIG["sector"]]
    condition: Annotated["TreeConditionEnum", TREE_FIELDS_CONFIG["condition"]]
    is_emergency: Annotated[bool, TREE_FIELDS_CONFIG["is_emergency"]]

    model_config = ConfigDict(from_attributes=True)
