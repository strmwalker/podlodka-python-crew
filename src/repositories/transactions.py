from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import functions

import models
import serializers


async def add_transaction(
    session: AsyncSession, transaction_in: serializers.TransactionIn, user: models.User
) -> models.Transaction:
    pass


async def get_paid_transactions(session: AsyncSession, bill_id: int, user_id: int):
    statement = select(functions.sum(models.Transaction.amount)).where(
        models.Transaction.bill_id == bill_id, models.Transaction.payer_id == user_id
    )
    result = await session.execute(statement)
    return result.scalar_one()
