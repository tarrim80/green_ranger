from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

ROLE_FIELDS_CONFIG = {
    "id": Field(description="Уникальный идентификатор", examples=[1, 2, 3]),
    "name": Field(
        description="Название роли пользователя",
        examples=["Куратор", "Волонтер"],
    ),
    "description": Field(
        description="Описание роли пользователя",
        examples=["Специалист ботанического сада"],
    ),
}


class RoleBase(BaseModel):
    name: Annotated[
        str,
        ROLE_FIELDS_CONFIG["name"],
    ]
    description: Annotated[
        str | None,
        ROLE_FIELDS_CONFIG["description"],
    ]


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Annotated[
        str | None,
        ROLE_FIELDS_CONFIG["name"],
    ] = None
    description: Annotated[
        str | None,
        ROLE_FIELDS_CONFIG["description"],
    ] = None


class RoleRead(RoleBase):
    id: Annotated[int, ROLE_FIELDS_CONFIG["id"]]

    model_config = ConfigDict(from_attributes=True)
