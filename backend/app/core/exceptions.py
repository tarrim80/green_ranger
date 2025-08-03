class AppException(Exception):
    """Базовое исключение для приложения."""

    pass


class FileProcessingError(AppException):
    """Исключение, возникающее при ошибке обработки файла."""

    pass


class DefectTypeCreationError(AppException):
    """Исключение, возникающее при ошибке создания Вида дефекта."""

    pass


class DefectTypeUpdatingError(AppException):
    """Исключение, возникающее при ошибке обновления Вида дефекта."""

    pass


class DefectTypeRemovingError(AppException):
    """Исключение, возникающее при ошибке удаления Вида дефекта."""

    pass


class SurveyDefectCreationError(AppException):
    """Исключение, возникающее при ошибке создания Дефекта."""

    pass


class SurveyDefectUpdatingError(AppException):
    """Исключение, возникающее при ошибке обновления Дефекта."""

    pass


class SurveyDefectRemovingError(AppException):
    """Исключение, возникающее при ошибке удаления Дефекта."""

    pass


class SurveyCreationError(AppException):
    """Исключение, возникающее при ошибке создания Обследования."""

    pass


class SurveyUpdatingError(AppException):
    """Исключение, возникающее при ошибке обновления Обследования."""

    pass


class SurveyRemovingError(AppException):
    """Исключение, возникающее при ошибке удаления Обследования."""

    pass


class SectorCreationError(AppException):
    """Исключение, возникающее при ошибке создания Учётного участка."""

    pass


class SectorUpdatingError(AppException):
    """Исключение, возникающее при ошибке обновления Учётного участка."""

    pass


class SectorRemovingError(AppException):
    """Исключение, возникающее при ошибке удаления Учётного участка."""

    pass


class TeamCreationError(AppException):
    """Исключение, возникающее при ошибке создания Команды волонтёров."""

    pass


class TeamUpdatingError(AppException):
    """Исключение, возникающее при ошибке обновления Команды волонтёров."""

    pass


class TeamRemovingError(AppException):
    """Исключение, возникающее при ошибке удаления Команды волонтёров."""

    pass


class TreeCreationError(AppException):
    """Исключение, возникающее при ошибке создания Растения (Дерева)."""

    pass


class TreeUpdatingError(AppException):
    """Исключение, возникающее при ошибке обновления Растения (Дерева)."""

    pass


class TreeRemovingError(AppException):
    """Исключение, возникающее при ошибке удаления Растения (Дерева)."""

    pass


class PhotoCreationError(AppException):
    """Исключение, возникающее при ошибке создания Фотографии/Изображения."""

    pass


class PhotoUpdatingError(AppException):
    """Исключение, возникающее при ошибке обновления Фотографии/Изображения."""

    pass


class PhotoRemovingError(AppException):
    """Исключение, возникающее при ошибке удаления Фотографии/Изображения."""

    pass


class NotFoundError(AppException):
    """Исключение для случаев, когда объект не найден в БД."""

    pass


class NotAllowedError(AppException):
    """
    Исключение для запрещенных операций (например, удаление связанных данных).
    """

    pass


class AuthorizedError(AppException):
    """Исключение, связанное с ошибками авторизации."""

    pass


class PermissionDenniedError(AppException):
    """Исключение, возникающее при нехватке прав доступа к объекту."""

    pass


class ExceptionDetails:
    """Хранилище текстовых сообщений для исключений."""

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
    NO_RIGHT_FOR_ACTION = "Нет прав для этого действия"
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
    TREE_LOCATION_OUTSIDE_OF_SECTOR = (
        "Координаты дерева находятся вне границ указанного участка."
    )
