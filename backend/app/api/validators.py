from app.api.constants import ValidationMessages
from app.models import User


def validate_leader_is_member(leader_id: int, member_ids: list[int]) -> None:
    """Проверяет, что назначаемый лидер команды является ее участником."""
    if leader_id not in member_ids:
        raise ValueError(ValidationMessages.LEADER_NOT_A_MEMBER)


def validate_user_is_free_for_team(user: User) -> None:
    """Проверяет, что пользователь не состоит ни в какой команде."""
    if user.team_id is not None:
        raise ValueError(ValidationMessages.NOT_ALLOWED_ADD_OTHER_TEAM)


def validate_photo_links(data: dict) -> None:
    """Проверяет, что фотография связана хотя бы с одной сущностью."""
    if not any(
        (
            data.get("defect_type_id"),
            data.get("survey_id"),
            data.get("survey_defect_id"),
        )
    ):
        raise ValueError(ValidationMessages.PHOTO_HAS_NO_LINKS)
