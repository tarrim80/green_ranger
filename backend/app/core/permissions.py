from typing import Type

from fastapi import Depends, HTTPException, status

from app.core.user import current_user
from app.models import User

from .exceptions import ExceptionDetails


class BasePermission:
    async def has_permission(self, user: User) -> bool:
        return True


class IsAdmin(BasePermission):
    async def has_permission(self, user: User) -> bool:
        return any(
            [role.name.lower() == "администратор" for role in user.roles]
        )


class IsCurator(BasePermission):
    async def has_permission(self, user: User) -> bool:
        return any([role.name.lower() == "куратор" for role in user.roles])


class IsVolunteer(BasePermission):
    async def has_permission(self, user: User) -> bool:
        return any(
            [
                (
                    role.name.lower() == "волонтер"
                    or role.name.lower() == "волонтёр"
                )
                for role in user.roles
            ]
        )


class IsAdminOrCurator(BasePermission):
    async def has_permission(self, user: User) -> bool:
        return any(
            [
                (
                    role.name.lower() == "администратор"
                    or role.name.lower() == "куратор"
                )
                for role in user.roles
            ]
        )


def permission_dependency(permission: Type[BasePermission]):
    async def check_permission(
        user: User = Depends(dependency=current_user),
    ) -> bool:
        checker = permission()
        if not await checker.has_permission(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ExceptionDetails.ACCESS_FORBIDDEN,
            )
        return True

    return check_permission
