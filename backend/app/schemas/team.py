from pydantic import BaseModel, ConfigDict, model_validator

from app.api.validators import validate_leader_is_member
from app.schemas.user import UserShortRead


class TeamBase(BaseModel):
    name: str
    leader_id: int


class TeamCreate(TeamBase):
    # @model_validator(mode="after")
    # def check_leader_in_members(self) -> "TeamCreate":
    #     validate_leader_is_member(
    #         leader_id=self.leader_id, member_ids=self.member_ids
    #     )
    #     return self
    pass


class TeamUpdate(BaseModel):
    name: str | None = None
    leader_id: int | None = None


class TeamShortRead(BaseModel):
    id: int
    name: str
    leader: UserShortRead

    model_config = ConfigDict(from_attributes=True)


class TeamRead(TeamShortRead):
    members: list[UserShortRead]
