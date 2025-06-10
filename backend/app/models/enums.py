from enum import Enum


class TreeConditionEnum(str, Enum):
    HEALTHY = "Здоровые"
    WEAKENED = "Ослабленные"
    OPPRESSED = "Угнетенные"
    DRYING = "Усыхающие"
    EMERGENCY_DEAD = "Аварийное"  # сухостой


class TicketStatusEnum(str, Enum):
    NEW = "Новая"
    CONFIRMED = "Принята в работу"
    IN_PROGRESS = "В обработке"
    COMPLETED = "Завершена"
    POSTPONED = "Отложена"
    CANCELLED = "Отменена"
    REMOVED = "Растение удалено"


class DamageStatusEnum(str, Enum):
    ACTIVE = "Активно"
    PROCESSING = "В процессе лечения"
    RESOLVED = "Устранено"
    NO_ACTION_NEEDED = "Не требует вмешательства"
    MONITORING = "Мониторинг"
