from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import SurveyStatusEnum, TreeConditionEnum
from app.schemas.photo import PhotoRead
from app.schemas.survey_defect import SurveyDefectCreate, SurveyDefectRead
from app.schemas.user import UserShortRead


class SurveyBase(BaseModel):
    age: int | None
    height: float | None
    diameter: float | None
    trunk_count: int
    condition: TreeConditionEnum
    is_emergency_report: bool
    note: str | None


class SurveyCreate(SurveyBase):
    tree_id: int
    tree_photo_ids: list[int] = Field(default_factory=list)
    survey_defects: list[SurveyDefectCreate] = Field(default_factory=list)


class SurveyUpdate(BaseModel):
    tree_id: int | None = None
    age: int | None = None
    height: float | None = None
    diameter: float | None = None
    trunk_count: int | None = None
    condition: TreeConditionEnum | None = None
    is_emergency_report: bool | None = None
    note: str | None = None
    survey_status: SurveyStatusEnum | None = None


class SurveyRead(SurveyBase):
    id: int
    tree_id: int
    survey_status: SurveyStatusEnum
    created_at: datetime
    updated_at: datetime
    author: UserShortRead
    tree_photos: list[PhotoRead]
    survey_defects: list[SurveyDefectRead]

    model_config = ConfigDict(from_attributes=True)
