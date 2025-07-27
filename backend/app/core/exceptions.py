class AppException(Exception):
    pass


class FileProcessingError(AppException):
    pass


class DefectTypeCreationError(AppException):
    pass


class DefectTypeUpdatingError(AppException):
    pass


class DefectTypeRemovingError(AppException):
    pass


class SurveyDefectCreationError(AppException):
    pass


class SurveyDefectUpdatingError(AppException):
    pass


class SurveyDefectRemovingError(AppException):
    pass


class SurveyCreationError(AppException):
    pass


class SurveyUpdatingError(AppException):
    pass


class SurveyRemovingError(AppException):
    pass


class SectorCreationError(AppException):
    pass


class SectorUpdatingError(AppException):
    pass


class SectorRemovingError(AppException):
    pass


class TeamCreationError(AppException):
    pass


class TeamUpdatingError(AppException):
    pass


class TeamRemovingError(AppException):
    pass


class TreeCreationError(AppException):
    pass


class TreeUpdatingError(AppException):
    pass


class TreeRemovingError(AppException):
    pass


class PhotoCreationError(AppException):
    pass


class PhotoUpdatingError(AppException):
    pass


class PhotoRemovingError(AppException):
    pass


class RoleCreationError(AppException):
    pass


class RoleUpdatingError(AppException):
    pass


class RoleRemovingError(AppException):
    pass


class NotFoundError(AppException):
    pass


class NotAllowedError(AppException):
    pass


class AuthorizedError(AppException):
    pass


class ExceptionDetails:
    @staticmethod
    def get_not_found_detail(model_name: str, id: int) -> str:
        return f"Не найден объект: {model_name} с идентификатором {id}"

    ACCESS_FORBIDDEN = "Доступ запрещен"
    ALREADY_EXIST_DEFECT_TYPE_NAME = (
        "Вид дефекта с таким названием уже существует"
    )
    ALREADY_EXIST_SECTOR_NAME = (
        "Учетный участок с таким названием уже существует"
    )
    ALREADY_EXIST_TEAM_NAME = (
        "Команда волонтеров с таким названием уже существует"
    )
    FAILED_CREATE_DEFECT_TYPE = "Ошибка при создании вида дефекта"
    FAILED_CREATE_PHOTO = "Ошибка при создании и привязке фото"
    FAILED_CREATE_RECORD = "Ошибка при записи в базу данных"
    FAILED_UPDATE_RECORD = "Ошибка при изменении записи в базе данных"
    FAILED_CREATE_SURVEY = "Ошибка при создании обследования"
    FAILED_CREATE_SURVEY_DEFECT = "Ошибка при создании обнаруженного дефекта"
    FAILED_REMOVE_DEFECT_TYPE = "Ошибка при удалении вида дефекта"
    FAILED_REMOVE_PHOTO = "Ошибка при удалении фотографии"
    FAILED_REMOVE_RECORD = "Ошибка при удалении записи из базы данных"
    FAILED_REMOVE_SURVEY = "Ошибка при удалении обследования"
    FAILED_ROMOVE_SURVEY_DEFECT = "Ошибка при удалении обнаруженного дефекта"
    FAILED_TO_PROCESSING_FILE = "Ошибка при обработке файла"
    INVALID_TOKEN = "Невалидный или просроченный refresh-токен"
    INVALID_USER_ID = (
        "Не удалось получить идентификатор пользователя из токена"
    )
    INVALID_USERNAME_OR_PASSWORD = "Неверное имя пользователя или пароль"
    NOT_ALLOWED_ADD_OTHER_TEAM = "Невозможно добавить в команду пользователя, состоящего в другой команде. Сначала исключите из другой команды."
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
    NOT_FOUND_OR_NOT_ACTIVE_USER = "Пользователь не найден или неактивен"
    NOT_FOUND_SOME_USERS = "Не найдены один или несколько пользователей"
