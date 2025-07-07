from app.schemas import DefectStatusEnum, SurveyStatusEnum, TreeConditionEnum

MAX_PHOTO_PX = (1920, 1080)
FORMAT_PHOTO = "JPEG"
PHOTO_QUALITY = 80
DEFAULT_LIMIT = 100


class ExceptionDetails:
    @staticmethod
    def get_not_found_detail(model_name: str, id: int) -> str:
        return f"Не найден объект: {model_name} с идентификатором {id}"

    FAILED_TO_PROCESSING_FILE = "Ошибка при обработке файла"
    FAILED_CREATE_RECORD = "Ошибка при записи в базу данных"
    FAILED_CREATE_DEFECT_TYPE = "Ошибка при создании вида дефекта"
    FAILED_REMOVE_DEFECT_TYPE = "Ошибка при удалении вида дефекта"
    FAILED_CREATE_SURVEY = "Ошибка при создании обследования"
    FAILED_REMOVE_SURVEY = "Ошибка при удалении обследования"
    FAILED_CREATE_SURVEY_DEFECT = "Ошибка при создании обнаруженного дефекта"
    FAILED_ROMOVE_SURVEY_DEFECT = "Ошибка при удалении обнаруженного дефекта"
    FAILED_CREATE_PHOTO = "Ошибка при создании и привязке фото"
    FAILED_REMOVE_PHOTO = "Ошибка при удалении фотографии"
    FAILED_REMOVE_RECORD = "Ошибка при удалении записи из базы данных"
    ALREADY_EXIST_DEFECT_TYPE_NAME = (
        "Вид дефекта с таким названием уже существует"
    )
    ALREADY_EXIST_TEAM_NAME = (
        "Команда волонтеров с таким названием уже существует"
    )
    ALREADY_EXIST_SECTOR_NAME = (
        "Учетный участок с таким названием уже существует"
    )
    NOT_ALLOWED_REMOVE_SECTOR_WITH_TREES = (
        "Невозможно удалить участок, на котором зарегистрированы растения"
    )
    NOT_ALLOWED_REMOVE_SECTOR_WITH_TEAM = (
        "Невозможно удалить участок, за которым закреплена команда волонтеров"
    )
    NOT_ALLOWED_REMOVE_TEAM_WITH_USERS = (
        "Невозможно удалить команду, к которой прикреплены волонтеры"
    )

    NOT_ALLOWED_REMOVE_TREES = 'Не удаляйте растение. Установите состояние "Растение удалено" или "Погибшее"'
    NOT_ALLOWED_REMOVE_USERS = "Удаление пользователей запрещено!"
    NOT_ALLOWED_REMOVE_LEADER_TEAM = "Невозможно исключить лидера из команды. Сначала назначьте нового лидера команды."
    NOT_ALLOWED_ADD_OTHER_TEAM = "Невозможно добавить в команду пользователя, состоящего в другой команде. Сначала исключите из другой команды."
    NOT_FOUND_SOME_USERS = "Не найдены один или несколько пользователей"


class ValidationMessages:
    LEADER_NOT_A_MEMBER = "Лидер команды должен входить в список участников"
    PHOTO_HAS_NO_LINKS = (
        "Фотография должна быть связана хотя бы с одним объектом "
        "(тип дефекта, обследование или дефект обследования)."
    )


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
