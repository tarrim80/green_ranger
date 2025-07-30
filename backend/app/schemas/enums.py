from enum import StrEnum


class RoleEnum(StrEnum):
    """Роли пользователей."""

    ADMIN = "Администратор"
    CURATOR = "Куратор"
    VOLUNTEER = "Волонтёр"


class TreeConditionEnum(StrEnum):
    """Состояния растения. КСО."""

    HEALTHY = "Здоровое"
    WEAKENED = "Ослабленное"
    OPPRESSED = "Угнетенное"
    DRYING = "Усыхающее"
    DEAD = "Погибшее"
    REMOVED = "Растение удалено"


class SurveyStatusEnum(StrEnum):
    """Статусы обследования."""

    ON_REVIEW = "На рассмотрении"
    NEEDS_CORRECTION = "На доработке"
    APPROVED = "Одобрено"
    REJECTED = "Отклонено"


class DefectStatusEnum(StrEnum):
    """Статусы (состояния) конкретных дефектов."""

    ACTIVE = "Актуален"
    IN_PROCESSING = "В работе"
    RESOLVED = "Устранён"
    NO_ACTION_NEEDED = "Не требует действий"
    ON_MONITORING = "На наблюдении"
    # TODO: (Требует миграции) Добавить "Не подтверждён"
