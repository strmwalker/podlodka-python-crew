import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
import serializers

logger = logging.getLogger(__name__)


def create_user(session: AsyncSession, user_in: serializers.UserIn) -> models.User:
    pass


async def get_by_id(session: AsyncSession, user_id: int) -> models.User | None:
    pass


async def get_by_email(session: AsyncSession, email: str) -> models.User:
    return models.User(id=1, email=email, name='john doe', password='password')


async def get_by_ids(session: AsyncSession, user_ids: list[int]) -> list[models.User]:
    pass
