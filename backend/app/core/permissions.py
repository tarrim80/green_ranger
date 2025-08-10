from typing import Generic, TypeVar

from fastapi import Depends, HTTPException, status

from app.core.exceptions import ExceptionDetails
from app.core.user import current_user
from app.models import Sector, Survey, SurveyDefect, Tree, User
from app.schemas.enums import RoleEnum, SurveyStatusEnum

T = TypeVar("T")


class BasePermission:
    """Абстрактный базовый класс для ролевых разрешений."""

    async def has_permission(self, user: User) -> bool:
        """Проверяет, имеет ли пользователь необходимые права."""
        return False


class IsAdmin(BasePermission):
    """Разрешение для пользователей с ролью 'Администратор'."""

    async def has_permission(self, user: User) -> bool:
        """Проверяет наличие роли 'Администратор'."""
        has_role = user.role == RoleEnum.ADMIN
        return has_role or await super().has_permission(user)


class IsCurator(IsAdmin):
    """Разрешение для пользователей с ролью 'Куратор' и выше."""

    async def has_permission(self, user: User) -> bool:
        """Проверяет наличие роли 'Куратор' или более высокой."""
        has_role = user.role == RoleEnum.CURATOR
        return has_role or await super().has_permission(user)


class IsVolunteer(IsCurator):
    """Разрешение для пользователей с ролью 'Волонтер' и выше."""

    async def has_permission(self, user: User) -> bool:
        """Проверяет наличие роли 'Волонтер' или более высокой."""
        has_role = user.role == RoleEnum.VOLUNTEER
        return has_role or await super().has_permission(user)


class IsStrictlyVolunteer(BasePermission):
    """
    Разрешение ТОЛЬКО для пользователей с ролью 'Волонтёр'.
    Не включает Кураторов и Администраторов.
    """

    async def has_permission(self, user: User) -> bool:
        """Проверяет наличие роли 'Волонтер'."""
        return user.role == RoleEnum.VOLUNTEER


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

        match user.role:
            case RoleEnum.ADMIN:
                return True

            case RoleEnum.CURATOR:
                return obj.tree.sector.curator_id == user.id

            case RoleEnum.VOLUNTEER:
                is_owner = obj.author_id == user.id
                is_status_correct = obj.survey_status in (
                    SurveyStatusEnum.ON_REVIEW,
                    SurveyStatusEnum.NEEDS_CORRECTION,
                )
                return is_owner and is_status_correct

            case _:
                return False


class IsSurveyDefectOwnerOrCurator(BaseObjectPermission[SurveyDefect]):
    """
    Проверяет права на изменение конкретного дефекта.

    Доступ разрешен администраторам, кураторам своего участка,
    а также авторам обследования с корректным статусом.
    """

    async def has_obj_permission(self, user: User, obj: SurveyDefect) -> bool:
        """Проверяет, что пользователь является владельцем или куратором."""

        match user.role:
            case RoleEnum.ADMIN:
                return True

            case RoleEnum.CURATOR:
                return obj.survey.tree.sector.curator_id == user.id

            case RoleEnum.VOLUNTEER:
                is_owner = obj.survey.author_id == user.id
                is_status_correct = obj.survey.survey_status in (
                    SurveyStatusEnum.ON_REVIEW,
                    SurveyStatusEnum.NEEDS_CORRECTION,
                )
                return is_owner and is_status_correct

            case _:
                return False


class IsTreeCuratorOrCorrectTeam(BaseObjectPermission[Tree]):
    """
    Проверяет права на изменение Растения.

    Доступ разрешен администраторам, кураторам своего участка
    и волотерам входящим в команду, закрепленную за участком.
    """

    async def has_obj_permission(self, user: User, obj: Tree) -> bool:
        """
        Проверяет, что пользователь является куратором участка размещения
        растения, или входит в команду закрепленную за участком.
        """

        match user.role:
            case RoleEnum.ADMIN:
                return True

            case RoleEnum.CURATOR:
                return obj.sector.curator_id == user.id

            case RoleEnum.VOLUNTEER:
                return user.team == obj.sector.team != None

            case _:
                return False


class IsSectorCuratorOrCorrectTeam(BaseObjectPermission[Sector]):
    """
    Проверяет права на создание Растения.

    Доступ разрешен администраторам, кураторам своего участка
    и волотерам входящим в команду, закрепленную за участком.
    """

    async def has_obj_permission(self, user: User, obj: Sector) -> bool:
        """
        Проверяет, что пользователь является куратором участка размещения
        растения, или входит в команду закрепленную за участком.
        """

        match user.role:
            case RoleEnum.ADMIN:
                return True

            case RoleEnum.CURATOR:
                return obj.curator_id == user.id

            case RoleEnum.VOLUNTEER:
                return user.team == obj.team != None

            case _:
                return False


class IsSectorCurator(BaseObjectPermission[Sector]):
    """
    Проверяет права на изменение Учетного участка.

    Доступ разрешен администраторам и кураторам своего участка.
    """

    async def has_obj_permission(self, user: User, obj: Sector) -> bool:
        """Проверяет, что пользователь является куратором данного участка."""

        match user.role:
            case RoleEnum.ADMIN:
                return True

            case RoleEnum.CURATOR:
                return obj.curator_id == user.id

            case _:
                return False


def permission_dependency(permission: type[BasePermission]):
    """Создает зависимость FastAPI для проверки ролевых разрешений."""

    async def check_permission(user: User = Depends(current_user)):
        """Выполняет проверку прав."""
        checker = permission()
        if not await checker.has_permission(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ExceptionDetails.ACCESS_FORBIDDEN,
            )

    return check_permission
