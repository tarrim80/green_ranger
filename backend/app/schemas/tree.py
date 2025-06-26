from datetime import datetime
from typing import TYPE_CHECKING

from geojson_pydantic import Point
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from app.schemas import SectorShortRead, TreeConditionEnum, UserShortRead


class TreeBase(BaseModel):
    planting: str
    species: str
    description: str
    location: Point
    azimuth: float | None
    distance: float | None
    condition: "TreeConditionEnum"
    is_emergency: bool


class TreeCreate(TreeBase):
    sector_id: int


class TreeUpdate(BaseModel):
    planting: str | None = None
    species: str | None = None
    description: str | None = None
    location: Point | None = None
    azimuth: float | None = None
    distance: float | None = None
    sector_id: int | None = None
    condition: "TreeConditionEnum | None" = None
    is_emergency: bool | None = None


class TreeRead(TreeBase):
    id: int
    sector: "SectorShortRead"
    author: "UserShortRead"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TreeShortRead(BaseModel):
    id: int
    location: Point
    condition: "TreeConditionEnum"
    is_emergency: bool

    model_config = ConfigDict(from_attributes=True)
