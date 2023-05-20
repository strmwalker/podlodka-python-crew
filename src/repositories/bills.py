from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import functions

import models


class Bill(BaseModel):
    description: str
    total_amount: float

    payer_id: int
    group_id: int

    shares: dict[int, float]


def create_bill(session: AsyncSession, bill_in: Bill) -> models.Bill:
    pass


async def get_bill(session: AsyncSession, bill_id: int) -> models.Bill | None:
    pass
