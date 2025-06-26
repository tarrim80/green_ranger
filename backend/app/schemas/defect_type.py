from pydantic import BaseModel, ConfigDict, Field

from app.schemas.photo import PhotoRead


class DefectTypeBase(BaseModel):
    name: str
    description: str | None = None


class DefectTypeCreate(DefectTypeBase):
    image_ids: list[int] = Field(default_factory=list)


class DefectTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    image_ids: list[int] | None = None


class DefectTypeShortRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class DefectTypeRead(DefectTypeBase):
    id: int
    images: list[PhotoRead]

    model_config = ConfigDict(from_attributes=True)
