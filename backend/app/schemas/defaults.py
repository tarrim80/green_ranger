from app.schemas import DefectStatusEnum, SurveyStatusEnum, TreeConditionEnum, RoleEnum



class SurveyDefaults:
    TRUNK_COUNT = 1
    CONDITION = TreeConditionEnum.HEALTHY
    IS_EMERGENCY_REPORT = False
    SURVEY_STATUS = SurveyStatusEnum.ON_REVIEW


class SurveyDefectDefaults:
    DEFECT_STATUS = DefectStatusEnum.ACTIVE


class SectorDefaults:
    COLOR = "#000000"


class TreeDefaults:
    CONDITION = TreeConditionEnum.HEALTHY
    IS_EMERGENCY = False

class UserDefaults:
    ROLE = RoleEnum.VOLUNTEER
