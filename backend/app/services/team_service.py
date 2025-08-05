from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from app.api.validators import validate_leader_is_member
from app.core.exceptions import (
    ExceptionDetails,
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
from app.schemas import RoleEnum, TeamCreate, TeamUpdate
from app.services.mixins import DeleteObjMixin


class TeamService:
    """Сервисный слой для управления командами волонтёров."""

    def __init__(
        self,
        repo: TeamRepository = Depends(),
        user_repo: UserRepository = Depends(),
    ) -> None:
        self.repo = repo
        self.user_repo = user_repo

    async def get_all_teams(self) -> list[Team]:
        """Получает список всех команд."""
        teams_db = await self.repo.get_multi()
        return list(teams_db)

    async def get_team(self, obj_id: int) -> Team:
        """Получает команду по ее идентификатору."""
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
        """Создает новую команду и привязывает к ней участников."""
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
        """Обновляет данные существующей команды."""
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
        """Удаляет команду с проверкой на наличие участников."""
        try:
            team = await self.repo.get(id=team_id)
            if not team:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(),
                        id=team_id,
                    )
                )
            if len(team.members) > 1:
                raise NotAllowedError(
                    ExceptionDetails.NOT_ALLOWED_REMOVE_TEAM_WITH_USERS
                )
            if len(team.members) == 1:
                if team.members[0].id != team.leader_id:
                    raise NotAllowedError(
                        ExceptionDetails.NOT_ALLOWED_REMOVE_TEAM_IF_USER_NOT_LEADER
                    )
            async with atomic_transaction(self.repo.session):
                if team.members:
                    setattr(team.members[0], "team_id", None)
                    self.repo.session.add(instance=team.members[0])
                await self.repo.remove(id=team_id)
        except NotFoundError as e:
            raise
        except NotAllowedError as e:
            raise
        except Exception as e:
            raise TeamRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_RECORD}: {e}"
            ) from e

    async def sync_members(self, team_id: int, member_ids: list[int]) -> Team:
        """Добавляет новых участников в команду и удаляет исключенных."""
        try:
            team_db = await self.repo.get(id=team_id)
            if not team_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(), id=team_id
                    )
                )
            new_member_ids_set = set(member_ids)
            current_member_ids_set = {member.id for member in team_db.members}
            ids_to_add = new_member_ids_set - current_member_ids_set
            ids_to_remove = current_member_ids_set - new_member_ids_set
            if team_db.leader_id in ids_to_remove:
                raise NotAllowedError(
                    ExceptionDetails.NOT_ALLOWED_REMOVE_LEADER_TEAM
                )
            async with atomic_transaction(session=self.repo.session):
                if ids_to_add:
                    members_to_add = await self.user_repo.get_by_ids(
                        ids=list(ids_to_add)
                    )
                    if len(members_to_add) != len(ids_to_add):
                        raise NotFoundError(
                            ExceptionDetails.NOT_FOUND_SOME_USERS
                        )
                    for member in members_to_add:
                        if member.role != RoleEnum.VOLUNTEER:
                            raise NotAllowedError(
                                ExceptionDetails.NOT_ALLOWED_ADD_NO_VOLUNTEER
                            )
                        if member.team_id is not None:
                            raise NotAllowedError(
                                ExceptionDetails.NOT_ALLOWED_ADD_OTHER_TEAM
                            )
                        setattr(member, "team_id", team_id)
                        self.repo.session.add(instance=member)
                if ids_to_remove:
                    members_to_remove = await self.user_repo.get_by_ids(
                        ids=list(ids_to_remove)
                    )
                    for member in members_to_remove:
                        setattr(member, "team_id", None)
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
