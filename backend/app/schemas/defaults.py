from app.schemas import (
    DefectStatusEnum,
    RoleEnum,
    SurveyStatusEnum,
    TreeConditionEnum,
)


class SurveyDefaults:
    """Значения по умолчанию для обследований."""

    TRUNK_COUNT = 1
    CONDITION = TreeConditionEnum.HEALTHY
    IS_EMERGENCY_REPORT = False
    SURVEY_STATUS = SurveyStatusEnum.ON_REVIEW


class SurveyDefectDefaults:
    """Значения по умолчанию для обнаруженных при обследовании дефектов."""

    DEFECT_STATUS = DefectStatusEnum.ACTIVE


class SectorDefaults:
    """Значения по умолчанию для учетных участков."""

    COLOR = "#000000"


class TreeDefaults:
    """Значения по умолчанию для растений."""

    CONDITION = TreeConditionEnum.HEALTHY
    IS_EMERGENCY = False


class UserDefaults:
    """Значения по умолчанию для пользователей."""

    ROLE = RoleEnum.VOLUNTEER
