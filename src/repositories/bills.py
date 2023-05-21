from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import functions

import models
import repositories.users


class Bill(BaseModel):
    description: str
    total_amount: float

    payer_id: int
    group_id: int

    amounts: dict[int, float]


async def create_bill(session: AsyncSession, bill_in: Bill) -> models.Bill:
    bill = models.Bill(
        description=bill_in.description,
        total_amount=bill_in.total_amount,
        payer_id=bill_in.payer_id,
        group_id=bill_in.group_id,
    )
    users = await repositories.users.get_by_ids(session, [user_id for user_id in bill_in.amounts])
    bill.shares = [models.BillShare(user=user, amount=bill_in.amounts[user.id]) for user in users]
    session.add(bill)
    return bill


def create_bill(session: AsyncSession, bill_in: Bill) -> models.Bill:
    bill = models.Bill(
        description=bill_in.description,
        total_amount=bill_in.total_amount,
        payer_id=bill_in.payer_id,
        group_id=bill_in.group_id,
    )
    bill.shares = [models.BillShare(user_id=user_id, amount=amount) for user_id, amount in bill_in.amounts]
    session.add(bill)
    return bill


async def get_bill(session: AsyncSession, bill_id: int) -> models.Bill | None:
    return await session.get(models.Bill, bill_id)


async def get_participant(
    session: AsyncSession, bill_id: int, user_id: int
) -> models.BillShare | None:
    return await session.get(models.BillShare, {'bill_id': bill_id, 'user_id': user_id})
