import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import models
import repositories
import serializers

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    pass


class NotFoundError(Exception):
    pass


class AuthError(Exception):
    pass


async def create_user(user_in: serializers.UserIn, session: AsyncSession) -> models.User:
    pass


async def create_group(
    group_in: serializers.GroupIn, user: models.User, session: AsyncSession
) -> models.Group:
    pass


async def get_group(
    group_id: int, user: models.User, session: AsyncSession
) -> models.Group | None:
    """Get group and test for membership"""
    pass


async def add_member(
    user_id: int, group_id: int, session: AsyncSession
) -> models.Group | None:
    pass


async def create_bill(
    bill_in: serializers.BillIn, user: models.User, session: AsyncSession
) -> models.Bill:
    pass

async def get_bill(
    bill_id: int, user: models.User, session: AsyncSession
) -> models.Bill | None:
    pass


async def get_amount_owed(bill_id: int, user: models.User, session: AsyncSession):
    raise NotImplementedError()


async def create_transaction(
    transaction_in: serializers.TransactionIn, user: models.User, session: AsyncSession
):
    await get_bill(transaction_in.bill_id, user, session)
    transaction = await repositories.transactions.add_transaction(
        session, transaction_in, user
    )
    await session.commit()
    return transaction
