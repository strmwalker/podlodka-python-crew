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
    pass


async def get_by_id(session: AsyncSession, group_id: int) -> models.Group | None:
    pass
