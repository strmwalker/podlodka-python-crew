from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import functions

import models
import serializers


async def add_transaction(
    session: AsyncSession, transaction_in: serializers.TransactionIn, user: models.User
) -> models.Transaction:
    transaction = models.Transaction(
        amount=transaction_in.amount,
        payer=user,
        bill_id=transaction_in.bill_id,
        recipient_id=transaction_in.recipient_id,
        description=transaction_in.description,
    )
    session.add(transaction)
    return transaction


async def get_paid_transactions(session: AsyncSession, bill_id: int, user_id: int):
    statement = select(functions.sum(models.Transaction.amount)).where(
        models.Transaction.bill_id == bill_id, models.Transaction.payer_id == user_id
    )
    result = await session.execute(statement)
    return result.scalar_one()
