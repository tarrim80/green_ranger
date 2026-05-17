from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from app.services.validators import (
    validate_leader_is_member,
    validate_user_is_free_for_team,
)
from app.core.exceptions import (
    ExceptionDetails,
    NotAllowedError,
    NotFoundError,
    TeamCreationError,
    TeamRemovingError,
    TeamUpdatingError,
)
from app.core.permissions import IsStrictlyVolunteer
from app.core.transaction_manager import atomic_transaction
from app.models import Team, User
from app.repositories.team import TeamRepository
from app.repositories.user import UserRepository
from app.schemas import TeamCreate, TeamUpdate


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

    async def create_team(self, team_in: TeamCreate) -> Team:
        """Создает новую команду и привязывает к ней участников."""
        try:
            leader_id = team_in.leader_id
            leader = await self.user_repo.get(id=leader_id)
            if not leader:
                raise TeamCreationError(ExceptionDetails.FAILED_CREATE_RECORD)
            member_ids = team_in.member_ids

            validate_leader_is_member(
                leader_id=leader_id, member_ids=member_ids
            )
            members = await self._validate_and_get_new_members(
                member_ids=member_ids
            )

            async with atomic_transaction(session=self.repo.session):
                team_data = team_in.model_dump(exclude={"member_ids"})
                new_team = Team(**team_data)
                self.repo.session.add(instance=new_team)
                await self.repo.session.flush()
                for member in members:
                    setattr(member, "team_id", new_team.id)
                    self.repo.session.add(instance=member)
                await self.repo.session.refresh(
                    instance=new_team, attribute_names=["members", "leader"]
                )
            return new_team
        except NotAllowedError as e:
            raise
        except Exception as e:
            if isinstance(e, IntegrityError):
                raise TeamCreationError(
                    ExceptionDetails.ALREADY_EXIST_TEAM_NAME
                )
            raise TeamCreationError(
                f"{ExceptionDetails.FAILED_CREATE_RECORD}: {e}"
            )

    async def _validate_and_get_new_members(
        self, member_ids: list[int]
    ) -> list[User]:
        """
        Проверяет, могут ли пользователи быть добавлены в команду.
        """
        if not member_ids:
            return []

        members = await self.user_repo.get_by_ids(ids=member_ids)
        if len(members) != len(set(member_ids)):
            raise NotFoundError(ExceptionDetails.NOT_FOUND_SOME_USERS)

        for member in members:
            permission = await IsStrictlyVolunteer().has_permission(
                user=member
            )
            if not permission:
                raise NotAllowedError(
                    ExceptionDetails.NOT_ALLOWED_ADD_NO_VOLUNTEER
                )
            validate_user_is_free_for_team(user=member)

        return members

    async def _sync_members(
        self, *, team_db: Team, new_member_ids_set: set[int]
    ) -> None:
        """Синхронизирует состав участников команды."""
        current_member_ids_set = {member.id for member in team_db.members}
        ids_to_add = list(new_member_ids_set - current_member_ids_set)
        ids_to_remove = list(current_member_ids_set - new_member_ids_set)

        if ids_to_add:
            members_to_add = await self._validate_and_get_new_members(
                member_ids=ids_to_add
            )
            for member in members_to_add:
                setattr(member, "team_id", team_db.id)
                self.repo.session.add(instance=member)

        if ids_to_remove:
            members_to_remove = await self.user_repo.get_by_ids(
                ids=ids_to_remove
            )
            for member in members_to_remove:
                setattr(member, "team_id", None)
                self.repo.session.add(instance=member)

    async def update_team(self, team_db: Team, team_in: TeamUpdate) -> Team:
        """Обновляет данные существующей команды."""
        try:
            team_update_data = team_in.model_dump(exclude_unset=True)
            new_member_ids = team_update_data.get("member_ids")

            final_leader_id = team_update_data.get(
                "leader_id", team_db.leader_id
            )
            current_member_ids = {member.id for member in team_db.members}
            final_member_ids = (
                set(new_member_ids)
                if new_member_ids is not None
                else current_member_ids
            )

            if "leader_id" in team_update_data:
                if not await self.user_repo.get(id=final_leader_id):
                    raise TeamUpdatingError(
                        ExceptionDetails.FAILED_UPDATE_RECORD
                    )

            validate_leader_is_member(
                leader_id=final_leader_id, member_ids=list(final_member_ids)
            )

            async with atomic_transaction(session=self.repo.session):
                if new_member_ids is not None:
                    await self._sync_members(
                        team_db=team_db,
                        new_member_ids_set=final_member_ids,
                    )
                    team_update_data.pop("member_ids")

                await self.repo.session.flush()
                team_updated = await self.repo.update(
                    db_obj=team_db,
                    obj_in=TeamUpdate(**team_update_data),
                )
                await self.repo.session.refresh(
                    instance=team_updated,
                    attribute_names=["members", "leader"],
                )
            return team_updated
        except (ValueError, NotAllowedError) as e:
            raise
        except Exception as e:
            if isinstance(e, IntegrityError):
                raise TeamUpdatingError(
                    ExceptionDetails.ALREADY_EXIST_TEAM_NAME
                )
            raise TeamUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            )

    async def delete_team(self, team: Team) -> None:
        """Удаляет команду с проверкой на наличие участников."""
        try:
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
                await self.repo.remove(id=team.id)
        except NotAllowedError as e:
            raise
        except Exception as e:
            raise TeamRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_RECORD}: {e}"
            ) from e
