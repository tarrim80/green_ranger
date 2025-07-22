from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from app.api.validators import validate_leader_is_member
from app.core.constants import ExceptionDetails
from app.core.exceptions import (
    NotAllowedError,
    NotFoundError,
    TeamCreationError,
    TeamRemovingError,
    TeamUpdatingError,
)
from app.core.transaction_manager import atomic_transaction
from app.models import Team
from app.repositories.team import TeamRepository
from app.repositories.user import UserRepository
from app.schemas import TeamCreate, TeamUpdate
from app.services.mixins import DeleteObjMixin


class TeamService(DeleteObjMixin):
    def __init__(
        self,
        repo: TeamRepository = Depends(),
        user_repo: UserRepository = Depends(),
    ) -> None:
        self.repo = repo
        self.user_repo = user_repo

    async def get_all_teams(self) -> list[Team]:
        teams_db = await self.repo.get_multi()
        return list(teams_db)

    async def get_team(self, obj_id: int) -> Team:
        team_db = await self.repo.get(id=obj_id)
        if not team_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.repo.model.verbose_name(),
                    id=obj_id,
                )
            )
        return team_db

    async def create_team(self, team_in: TeamCreate) -> Team:
        try:
            leader_id = team_in.leader_id
            member_ids = team_in.member_ids
            team_data = team_in.model_dump(exclude={"member_ids"})
            leader = await self.user_repo.get(id=leader_id)
            members = await self.user_repo.get_by_ids(ids=member_ids)
            if not leader:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.user_repo.model.verbose_name(),
                        id=leader_id,
                    )
                )
            if len(members) != len(set(member_ids)):
                raise NotFoundError(ExceptionDetails.NOT_FOUND_SOME_USERS)
            async with atomic_transaction(session=self.repo.session):
                new_team = Team(**team_data)
                self.repo.session.add(instance=new_team)
                await self.repo.session.flush()
                for user in members:
                    setattr(user, "team_id", new_team.id)
                    self.repo.session.add(instance=user)
                await self.repo.session.refresh(
                    instance=new_team, attribute_names=["members", "leader"]
                )
            return new_team
        except NotFoundError:
            raise
        except Exception as e:
            if isinstance(e, IntegrityError):
                raise TeamCreationError(
                    ExceptionDetails.ALREADY_EXIST_TEAM_NAME
                )
            raise TeamCreationError(
                f"{ExceptionDetails.FAILED_CREATE_RECORD}: {e}"
            )

    async def update_team(self, team_id: int, team_in: TeamUpdate) -> Team:
        team_updated: Team
        try:
            async with atomic_transaction(session=self.repo.session):
                team_db = await self.repo.get(id=team_id)
                if not team_db:
                    raise NotFoundError(
                        ExceptionDetails.get_not_found_detail(
                            model_name=self.repo.model.verbose_name(),
                            id=team_id,
                        )
                    )
                team_update_data = team_in.model_dump(exclude_unset=True)
                leader_id: int | None = team_update_data.get("leader_id")
                if leader_id:
                    member_ids: list[int] = [
                        member.id for member in team_db.members
                    ]
                    leader = await self.user_repo.get(id=leader_id)
                    if not leader:
                        raise NotFoundError(
                            ExceptionDetails.get_not_found_detail(
                                model_name=self.user_repo.model.verbose_name(),
                                id=leader_id,
                            )
                        )
                    validate_leader_is_member(
                        leader_id=leader_id, member_ids=member_ids
                    )
                team_updated = await self.repo.update(
                    db_obj=team_db, obj_in=team_in
                )
                await self.repo.session.flush()
                await self.repo.session.refresh(instance=team_updated)
            return team_updated
        except (ValueError, NotFoundError):
            raise
        except Exception as e:
            if isinstance(e, IntegrityError):
                raise TeamUpdatingError(
                    ExceptionDetails.ALREADY_EXIST_TEAM_NAME
                )
            raise TeamUpdatingError(
                f"{ExceptionDetails.FAILED_CREATE_RECORD}: {e}"
            )

    async def delete_team(self, team_id: int) -> None:
        try:
            team = await self.repo.get(id=team_id)
            if not team:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(),
                        id=team_id,
                    )
                )
            if team.members:
                raise NotAllowedError(
                    ExceptionDetails.NOT_ALLOWED_REMOVE_TEAM_WITH_USERS
                )
            await self.delete_obj(obj_id=team_id)
        except NotFoundError as e:
            raise
        except NotAllowedError as e:
            raise
        except Exception as e:
            raise TeamRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_RECORD}: {e}"
            ) from e

    async def add_members(self, team_id: int, member_ids: list[int]) -> Team:
        try:
            member_ids = list(set(member_ids))
            team_db = await self.repo.get(id=team_id)
            if not team_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(), id=team_id
                    )
                )
            members = await self.user_repo.get_by_ids(ids=member_ids)
            if len(members) != len(member_ids):
                raise NotFoundError(ExceptionDetails.NOT_FOUND_SOME_USERS)
            members_to_add = []
            for member in members:
                if member.team_id is not None:
                    if member in team_db.members:
                        continue
                    raise NotAllowedError(
                        ExceptionDetails.NOT_ALLOWED_ADD_OTHER_TEAM
                    )
                members_to_add.append(member)
            async with atomic_transaction(session=self.repo.session):
                for member in members_to_add:
                    setattr(member, "team_id", team_id)
                    self.repo.session.add(instance=member)
            await self.repo.session.refresh(
                instance=team_db, attribute_names=["members", "leader"]
            )
            return team_db
        except (NotAllowedError, NotFoundError):
            raise
        except Exception as e:
            raise TeamCreationError(
                f"{ExceptionDetails.FAILED_CREATE_RECORD}: {e}"
            ) from e

    async def remove_members(
        self, team_id: int, member_ids: list[int]
    ) -> Team:
        try:
            member_ids = list(set(member_ids))
            team_db = await self.repo.get(id=team_id)
            if not team_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(), id=team_id
                    )
                )
            if team_db.leader_id in member_ids:
                raise NotAllowedError(
                    ExceptionDetails.NOT_ALLOWED_REMOVE_LEADER_TEAM
                )
            async with atomic_transaction(session=self.repo.session):
                for member in team_db.members:
                    if member.id not in member_ids:
                        continue
                    setattr(member, "team_id", None)
                    self.repo.session.add(instance=member)
            await self.repo.session.refresh(
                instance=team_db, attribute_names=["members", "leader"]
            )
            return team_db
        except (NotAllowedError, NotFoundError):
            raise
        except Exception as e:
            raise TeamRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_RECORD}: {e}"
            ) from e
