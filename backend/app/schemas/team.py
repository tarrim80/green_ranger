from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.services.validators import validate_leader_is_member
from app.schemas.sector import SectorShortRead
from app.schemas.user import UserShortRead

TEAM_FIELDS_CONFIG = {
    "id": Field(description="Уникальный идентификатор", examples=[1, 2, 3]),
    "name": Field(
        description="Название команды",
        examples=["Команда Петрова", "Команда Ахметовой"],
        max_length=50,
    ),
    "leader_id": Field(
        description="Идентификатор ID лидера (бригадира) команды",
        examples=[1, 2, 3],
    ),
    "leader": Field(
        description="Имя лидера команды",
        examples=["Улжан Ахметова"],
    ),
    "member_ids": Field(
        description="Список идентификаторов ID волонтеров команды",
        examples=[[1, 2, 3]],
    ),
    "members": Field(
        description="Список волонтеров команды",
        examples=[["Иван Петров", "Данияр Ермеков", "Улжан Ахметова"]],
    ),
    "sectors": Field(
        description="Список участков, за которыми закреплена команда",
        examples=[["Орхидные", "Северный", "3"]],
    ),
}


class TeamBase(BaseModel):
    """Базовая схема для команды."""

    name: Annotated[str, TEAM_FIELDS_CONFIG["name"]]
    leader_id: Annotated[int, TEAM_FIELDS_CONFIG["leader_id"]]
    member_ids: Annotated[list[int], TEAM_FIELDS_CONFIG["member_ids"]]


class TeamCreate(TeamBase):
    """Схема для создания команды с валидацией."""

    @model_validator(mode="after")
    def check_leader_in_members(self) -> "TeamCreate":
        validate_leader_is_member(
            leader_id=self.leader_id, member_ids=self.member_ids
        )
        return self

    pass


class TeamUpdate(BaseModel):
    """Схема для обновления команды."""

    name: Annotated[str | None, TEAM_FIELDS_CONFIG["name"]] = None
    leader_id: Annotated[int | None, TEAM_FIELDS_CONFIG["leader_id"]] = None
    member_ids: Annotated[
        list[int] | None, TEAM_FIELDS_CONFIG["member_ids"]
    ] = None


class TeamShortRead(BaseModel):
    """Схема для краткого представления команды."""

    id: Annotated[int, TEAM_FIELDS_CONFIG["id"]]
    name: Annotated[str, TEAM_FIELDS_CONFIG["name"]]
    leader: Annotated[UserShortRead, TEAM_FIELDS_CONFIG["leader"]]

    model_config = ConfigDict(from_attributes=True)


class TeamRead(TeamShortRead):
    """Схема для чтения команды с участниками."""

    members: Annotated[list[UserShortRead], TEAM_FIELDS_CONFIG["members"]]
    sectors: Annotated[list[SectorShortRead], TEAM_FIELDS_CONFIG["sectors"]]
