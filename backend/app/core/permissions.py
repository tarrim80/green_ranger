from typing import Generic, TypeVar

from fastapi import Depends, HTTPException, status

from app.core.exceptions import ExceptionDetails
from app.core.user import current_user
from app.models import Survey, SurveyDefect, Tree, User
from app.schemas.enums import RoleEnum, SurveyStatusEnum

T = TypeVar("T")


class BasePermission:
    """Абстрактный базовый класс для ролевых разрешений."""

    async def has_permission(self, user: User) -> bool:
        """Проверяет, имеет ли пользователь необходимые права."""
        return False


class IsVolunteer(BasePermission):
    """Разрешение для пользователей с ролью 'Волонтер' и выше."""

    async def has_permission(self, user: User) -> bool:
        """Проверяет наличие роли 'Волонтер' или более высокой."""
        has_role = user.role == RoleEnum.VOLUNTEER
        return has_role or await super().has_permission(user)


class IsCurator(IsVolunteer):
    """Разрешение для пользователей с ролью 'Куратор' и выше."""

    async def has_permission(self, user: User) -> bool:
        """Проверяет наличие роли 'Куратор' или более высокой."""
        has_role = user.role == RoleEnum.CURATOR
        return has_role or await super().has_permission(user)


class IsAdmin(IsCurator):
    """Разрешение для пользователей с ролью 'Администратор'."""

    async def has_permission(self, user: User) -> bool:
        """Проверяет наличие роли 'Администратор'."""
        has_role = user.role == RoleEnum.ADMIN
        return has_role or await super().has_permission(user)


class BaseObjectPermission(Generic[T]):
    """Абстрактный базовый класс для объектных разрешений."""

    async def has_obj_permission(self, user: User, obj: T) -> bool:
        """Проверяет, имеет ли пользователь права на доступ к объекту."""
        return False


class IsSurveyOwnerOrCurator(BaseObjectPermission[Survey]):
    """
    Проверяет права на изменение обследования.

    Доступ разрешен администраторам, кураторам своего участка,
    а также авторам обследования с корректным статусом.
    """

    async def has_obj_permission(self, user: User, obj: Survey) -> bool:
        """Проверяет, что пользователь является владельцем или куратором."""
        if user.role == RoleEnum.ADMIN:
            return True

        if user.role == RoleEnum.CURATOR:
            return obj.tree.sector.curator_id == user.id

        if user.role == RoleEnum.VOLUNTEER:
            is_owner = obj.author_id == user.id
            is_status_correct = obj.survey_status in (
                SurveyStatusEnum.ON_REVIEW,
                SurveyStatusEnum.NEEDS_CORRECTION,
            )
            return is_owner and is_status_correct

        return False


class IsSurveyDefectOwnerOrCurator(BaseObjectPermission[SurveyDefect]):
    """
    Проверяет права на изменение конкретного дефекта.

    Доступ разрешен администраторам, кураторам своего участка,
    а также авторам обследования с корректным статусом.
    """

    async def has_obj_permission(self, user: User, obj: SurveyDefect) -> bool:
        """Проверяет, что пользователь является владельцем или куратором."""
        if user.role == RoleEnum.ADMIN:
            return True

        if user.role == RoleEnum.CURATOR:
            return obj.survey.tree.sector.curator_id == user.id

        if user.role == RoleEnum.VOLUNTEER:
            is_owner = obj.survey.author_id == user.id
            is_status_correct = obj.survey.survey_status in (
                SurveyStatusEnum.ON_REVIEW,
                SurveyStatusEnum.NEEDS_CORRECTION,
            )
            return is_owner and is_status_correct

        return False


class IsTreeCuratorOrCorrectTeam(BaseObjectPermission[Tree]):
    """
    Проверяет права на изменение Растения.

    Доступ разрешен администраторам и кураторам своего участка.
    """

    async def has_obj_permission(self, user: User, obj: Tree) -> bool:
        """
        Проверяет, что пользователь является куратором участка размещения
        растения, или входит в команду закрепленную за участком.
        """
        if user.role == RoleEnum.ADMIN:
            return True

        if user.role == RoleEnum.CURATOR:
            return obj.sector.curator_id == user.id

        if user.role == RoleEnum.VOLUNTEER:
            return user.team == obj.sector.team

        return False


def permission_dependency(permission: type[BasePermission]):
    """Фабрика зависимостей для проверки ролевых разрешений."""

    async def check_permission(user: User = Depends(current_user)):
        """Выполняет проверку прав."""
        checker = permission()
        if not await checker.has_permission(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ExceptionDetails.ACCESS_FORBIDDEN,
            )

    return check_permission
