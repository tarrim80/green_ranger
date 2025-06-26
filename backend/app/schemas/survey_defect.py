from pydantic import BaseModel, ConfigDict, Field

from app.schemas import DefectStatusEnum, DefectTypeShortRead, PhotoRead


class SurveyDefectBase(BaseModel):
    defect_type_id: int
    description: str | None = None


class SurveyDefectCreate(SurveyDefectBase):
    photo_ids: list[int] = Field(default_factory=list)


class SurveyDefectUpdate(BaseModel):
    description: str | None = None
    defect_status: DefectStatusEnum | None = None


class SurveyDefectRead(BaseModel):
    id: int
    description: str | None
    defect_status: DefectStatusEnum
    photos: list[PhotoRead]
    defect_type: DefectTypeShortRead

    model_config = ConfigDict(from_attributes=True)
