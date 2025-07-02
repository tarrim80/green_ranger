MAX_PHOTO_PX = (1920, 1080)
FORMAT_PHOTO = "JPEG"
PHOTO_QUALITY = 80
DEFAULT_LIMIT = 100


class ExceptionDetails:
    @staticmethod
    def get_not_found_detail(model_name: str) -> str:
        return f"Не найден объект: {model_name}"

    FAILED_TO_PROCESSING_FILE = "Ошибка при обработке файла"
    FAILED_CREATE_RECORD = "Ошибка при записи в базу данных"
    FAILED_CREATE_DEFECT_TYPE = "Ошибка при создании вида дефекта"
    FAILED_CREATE_SURVEY_DEFECT = "Ошибка при создании обнаруженного дефекта"
    FAILED_CREATE_PHOTO = "Ошибка при создании и привязке фото"
    FAILED_REMOVE_RECORD = "Ошибка при удалении из базы данных"
    ALREADY_EXIST_DEFECT_TYPE_NAME = (
        "Вид дефекта с таким названием уже существует"
    )


class ValidationMessages:
    LEADER_NOT_A_MEMBER = "Лидер команды должен входить в список участников"
    PHOTO_HAS_NO_LINKS = (
        "Фотография должна быть связана хотя бы с одним объектом "
        "(тип дефекта, обследование или дефект обследования)."
    )
