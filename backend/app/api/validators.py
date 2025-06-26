def validate_leader_is_member(leader_id: int, member_ids: list[int]) -> None:
    if leader_id not in member_ids:
        raise ValueError("Лидер команды должен входить в список участников")
