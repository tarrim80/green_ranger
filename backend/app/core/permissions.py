from typing import Type

from fastapi import Depends, HTTPException, status

from app.core.exceptions import ExceptionDetails
from app.core.user import current_user
from app.models import User
from app.schemas.enums import RoleEnum


class BasePermission:
    async def has_permission(self, user: User) -> bool:
        return False


class IsVolunteer(BasePermission):
    async def has_permission(self, user: User) -> bool:
        return user.role == RoleEnum.VOLUNTEER or await super().has_permission(
            user
        )


class IsCurator(IsVolunteer):
    async def has_permission(self, user: User) -> bool:
        return user.role == RoleEnum.CURATOR or await super().has_permission(
            user
        )


class IsAdmin(IsCurator):
    async def has_permission(self, user: User) -> bool:
        return user.role == RoleEnum.ADMIN or await super().has_permission(
            user
        )


def permission_dependency(permission: Type[BasePermission]):
    async def check_permission(
        user: User = Depends(dependency=current_user),
    ):
        checker = permission()
        if not await checker.has_permission(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ExceptionDetails.ACCESS_FORBIDDEN,
            )

    return check_permission
