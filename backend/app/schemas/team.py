from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.api.validators import validate_leader_is_member
from app.schemas.user import UserShortRead

TEAM_FIELDS_CONFIG = {
    "id": Field(description="Уникальный идентификатор", examples=[1, 2, 3]),
    "name": Field(
        description="Название команды (по умолчанию по фамилии лидера)",
        examples=["Команда Петрова", "Команда Ахметовой"],
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
}


class TeamBase(BaseModel):
    name: Annotated[str | None, TEAM_FIELDS_CONFIG["name"]] = None
    leader_id: Annotated[int, TEAM_FIELDS_CONFIG["leader_id"]]
    member_ids: Annotated[list[int], TEAM_FIELDS_CONFIG["member_ids"]]


class TeamCreate(TeamBase):
    @model_validator(mode="after")
    def check_leader_in_members(self) -> "TeamCreate":
        validate_leader_is_member(
            leader_id=self.leader_id, member_ids=self.member_ids
        )
        return self

    pass


class TeamUpdate(BaseModel):
    name: Annotated[str | None, TEAM_FIELDS_CONFIG["name"]] = None
    leader_id: Annotated[int | None, TEAM_FIELDS_CONFIG["leader_id"]] = None


class TeamShortRead(BaseModel):
    id: Annotated[int, TEAM_FIELDS_CONFIG["id"]]
    name: Annotated[str, TEAM_FIELDS_CONFIG["name"]]
    leader: Annotated[UserShortRead, TEAM_FIELDS_CONFIG["leader"]]

    model_config = ConfigDict(from_attributes=True)


class TeamRead(TeamShortRead):
    members: Annotated[list[UserShortRead], TEAM_FIELDS_CONFIG["members"]]
