from app.schemas.defect_type import (
    DefectTypeCreate,
    DefectTypeRead,
    DefectTypeShortRead,
    DefectTypeUpdate,
)
from app.schemas.enums import (
    DefectStatusEnum,
    SurveyStatusEnum,
    TreeConditionEnum,
)
from app.schemas.photo import PhotoCreate, PhotoRead, PhotoUpdate
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate
from app.schemas.sector import (
    SectorCreate,
    SectorRead,
    SectorShortRead,
    SectorUpdate,
)
from app.schemas.survey import (
    SurveyCreate,
    SurveyRead,
    SurveyShortRead,
    SurveyUpdate,
)
from app.schemas.survey_defect import (
    SurveyDefectCreate,
    SurveyDefectRead,
    SurveyDefectUpdate,
)
from app.schemas.team import TeamCreate, TeamRead, TeamShortRead, TeamUpdate
from app.schemas.tree import (
    TreeCreate,
    TreeCreateWithAuthor,
    TreeRead,
    TreeShortRead,
    TreeUpdate,
)
from app.schemas.user import UserCreate, UserRead, UserShortRead, UserUpdate

all_schemas = [
    DefectTypeRead,
    PhotoRead,
    RoleRead,
    SectorRead,
    SectorShortRead,
    SurveyRead,
    SurveyShortRead,
    SurveyDefectRead,
    TeamRead,
    TeamShortRead,
    TreeRead,
    TreeShortRead,
    UserRead,
    UserShortRead,
    TreeCreate,
    TreeCreateWithAuthor,
    TreeUpdate,
]


for schema in all_schemas:
    if hasattr(schema, "model_rebuild"):
        schema.model_rebuild()
