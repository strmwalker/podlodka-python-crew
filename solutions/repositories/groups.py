from sqlalchemy.ext.asyncio import AsyncSession

import models
import serializers


async def create_group(
    session: AsyncSession, group_in: serializers.GroupIn
) -> models.Group:
    group = models.Group(name=group_in.name)
    member_ids = group_in.members or []
    members = await repositories.users.get_by_ids(session, member_ids)
    for member in members:
        group.members.append(member)
    return group
