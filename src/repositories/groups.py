import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import models
import repositories.users
import serializers

logger = logging.getLogger(__name__)


async def create_group(
    session: AsyncSession, group_in: serializers.GroupIn
) -> models.Group:
    group = models.Group(name=group_in.name)
    if group_in.members:
        group.members = await repositories.users.get_by_ids(session, group_in.members)
    session.add(group)
    return group


# async def create_group(
#     session: AsyncSession, name: str, member_ids: list[int] = None
# ) -> models.Group:
#     member_ids = member_ids or []
#     logger.info('member_ids %s', member_ids)
#     group = models.Group(name=name)
#     for member_id in member_ids:
#         # group.members.append(models.User(id=member_id))
#         session.add(models.Membership(group=group, user_id=member_id))
#     session.add(group)
#     return group


async def get_by_id(session: AsyncSession, group_id: int) -> models.Group | None:
    statement = (
        select(models.Group)
        .where(models.Group.id == group_id)
        .options(joinedload(models.Group.members))
    )
    return await session.scalar(statement)


# async def add_member(session: AsyncSession, group: models.Group, user: models.User):
#     membership = models.Membership(group_id=group.id, user_id=user.id)
#     session.add(membership)
#     group.members.append(membership)
#
#
# async def get_membership(
#     session: AsyncSession, user_id: int, group_id: int
# ) -> models.Membership | None:
#     return await session.get(
#         models.Membership, {'user_id': user_id, 'group_id': group_id}
#     )
