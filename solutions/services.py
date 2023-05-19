from sqlalchemy.ext.asyncio import AsyncSession


async def create_group(
    name: str, user: models.User, member_ids: list[int] | None, session: AsyncSession
):
    group = await repositories.groups.create_group(session, name, member_ids)
    if member_ids:
        members = await repositories.users.get_by_ids(session, member_ids)
        for member in members:
            session.add(models.Membership(user_id=member.id, group_id=group.id))
    session.add(models.Membership(user_id=user.id, group_id=group.id))
    await session.commit()
    await session.refresh(group)
    return group
