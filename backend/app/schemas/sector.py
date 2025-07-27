from typing import TYPE_CHECKING, Annotated

from geoalchemy2.elements import WKBElement
from geojson_pydantic import Polygon
from pydantic import BaseModel, ConfigDict, Field, field_validator
from shapely.geometry import mapping
from shapely.wkb import loads as wkb_loads

if TYPE_CHECKING:
    from app.schemas import TeamShortRead, UserShortRead


SECTOR_FIELDS_CONFIG = {
    "id": Field(description="Уникальный идентификатор", examples=[1, 2, 3]),
    "name": Field(
        description="Название (номер) учетного участка",
        examples=["Участок 1", "Участок степных растений"],
    ),
    "color": Field(
        description="Цвет границы участка на карте в hex формате",
        examples=["#0F3BEB", "#FF2503"],
    ),
    "geometry": Field(
        description="Полигон - границы участка",
    ),
    "curator_id": Field(
        description="Идентификатор ID куратора учетного участка",
        examples=[1, 2, 3],
    ),
    "curator": Field(
        description="Имя куратора учетного участка",
        examples=["Владимир Эпиктетов"],
    ),
    "team_id": Field(
        description="Идентификатор ID команды волонтеров, \
            назначенной на участок",
        examples=[1, 2, 3],
    ),
    "team": Field(
        description="Список волонтеров команды, назначенной на участок",
        examples=[["Иван Петров", "Данияр Ермеков", "Улжан Ахметова"]],
    ),
}


class SectorBase(BaseModel):
    name: Annotated[str, SECTOR_FIELDS_CONFIG["name"]]
    color: Annotated[str, SECTOR_FIELDS_CONFIG["color"]]
    geometry: Annotated[Polygon, SECTOR_FIELDS_CONFIG["geometry"]]


class SectorCreate(SectorBase):
    curator_id: Annotated[int, SECTOR_FIELDS_CONFIG["curator_id"]]
    team_id: Annotated[int | None, SECTOR_FIELDS_CONFIG["team_id"]]


class SectorUpdate(BaseModel):
    name: Annotated[str | None, SECTOR_FIELDS_CONFIG["name"]] = None
    color: Annotated[str | None, SECTOR_FIELDS_CONFIG["color"]] = None
    geometry: Annotated[Polygon | None, SECTOR_FIELDS_CONFIG["geometry"]] = (
        None
    )
    curator_id: Annotated[int | None, SECTOR_FIELDS_CONFIG["curator_id"]] = (
        None
    )
    team_id: Annotated[int | None, SECTOR_FIELDS_CONFIG["team_id"]] = None


class SectorRead(SectorBase):
    id: Annotated[int, SECTOR_FIELDS_CONFIG["id"]]
    curator: Annotated["UserShortRead", SECTOR_FIELDS_CONFIG["curator"]]
    team: Annotated["TeamShortRead | None", SECTOR_FIELDS_CONFIG["team"]] = (
        None
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator("geometry", mode="before")
    @classmethod
    def parse_geometry(cls, element: WKBElement | dict) -> dict:
        """Преобразует WKBElement из БД в GeoJSON-совместимый словарь."""
        if isinstance(element, WKBElement):
            return mapping(wkb_loads(element.data))
        return element


class SectorShortRead(BaseModel):
    id: Annotated[int, SECTOR_FIELDS_CONFIG["id"]]
    name: Annotated[str, SECTOR_FIELDS_CONFIG["name"]]
    color: Annotated[str, SECTOR_FIELDS_CONFIG["color"]]

    model_config = ConfigDict(from_attributes=True)
