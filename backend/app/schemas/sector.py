from typing import TYPE_CHECKING

from geojson_pydantic import Polygon
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from app.schemas import TeamShortRead, UserShortRead


class SectorBase(BaseModel):
    name: str
    color: str
    geometry: Polygon


class SectorCreate(SectorBase):
    curator_id: int
    team_id: int | None


class SectorUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    geometry: Polygon | None = None
    curator_id: int | None = None
    team_id: int | None = None


class SectorRead(SectorBase):
    id: int
    curator: "UserShortRead"
    team: "TeamShortRead"

    model_config = ConfigDict(from_attributes=True)


class SectorShortRead(BaseModel):
    id: int
    name: str
    color: str

    model_config = ConfigDict(from_attributes=True)
