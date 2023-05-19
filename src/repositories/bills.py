from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import functions

import models


async def get_bill(session: AsyncSession, bill_id: int) -> models.Bill | None:
    return await session.get(models.Bill, bill_id)


async def get_participant(
    session: AsyncSession, bill_id: int, user_id: int
) -> models.BillShare | None:
    return await session.get(models.BillShare, {'bill_id': bill_id, 'user_id': user_id})
