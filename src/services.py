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
    user = repositories.users.create_user(session, user_in)
    try:
        await session.commit()
    except IntegrityError:
        raise ServiceError('User already exists')
    return user


async def create_group(
    group_in: serializers.GroupIn, user: models.User, session: AsyncSession
) -> models.Group:
    group = await repositories.groups.create_group(session, group_in)
    group.members.append(user)
    await session.commit()
    return group


async def get_group(
    group_id: int, user: models.User, session: AsyncSession
) -> models.Group | None:
    """Get group and test for membership"""
    group = await repositories.groups.get_by_id(session, group_id)
    if not group:
        raise NotFoundError(f'Group id={group_id} not found')
    if user not in group.members:
        raise AuthError(f'User id={user.id} is not a member of group id={group.id}')
    return group


async def add_member(
    user_id: int, group_id: int, session: AsyncSession
) -> models.Group | None:
    user = await repositories.users.get_by_id(session, user_id)
    if not user:
        raise NotFoundError('User not found')
    group = await repositories.groups.get_by_id(session, group_id)
    if not group:
        raise NotFoundError('Group not found')
    group.members.append(user)
    await session.commit()
    # await session.refresh(group)
    return group


# async def create_bill(
#     bill_in: serializers.BillIn, user: models.User, session: AsyncSession
# ) -> models.Bill:
#     """
#     Version 0: All group members are participating in bill, current user is payer, no repository layer
#     """
#     group = await get_group(bill_in.group_id, user, session)
#
#     if bill_in.payer_id:
#         payer = await repositories.users.get_by_id(session, bill_in.payer_id)
#     else:
#         payer = user
#
#     shares = bill_in.shares or []
#     if shares:
#         participants = await repositories.users.get_by_ids(session, [s.user_id for s in shares])
#     else:
#         participants = [member for member in group.members if member is not payer]
#
#     defined_shares = [share for share in shares if share.amount]
#     defined_amounts = sum(share.amount for share in defined_shares)
#     default_amount = (bill_in.total_amount - defined_amounts) / (
#         len(participants) - len(defined_shares)
#         + 1  # payer
#     )
#     amounts = {share.user_id: share.amount or default_amount for share in shares}
#
#     bill = models.Bill(
#         description=bill_in.description,
#         total_amount=bill_in.total_amount,
#         payer=payer,
#         group=group,
#     )
#     for participant in participants:
#         share = models.BillShare(user=participant, amount=amounts[participant.id])
#         session.add(share)
#         bill.shares.append(share)
#
#     session.add(bill)
#     await session.commit()
#     return bill


async def create_bill(
    bill_in: serializers.BillIn, user: models.User, session: AsyncSession
) -> models.Bill:
    """
    Version 0: All group members are participating in bill, current user is payer, no repository layer
    """
    group = await get_group(bill_in.group_id, user, session)

    payer_id = bill_in.payer_id or user.id
    if bill_in.shares:
        participant_ids = [share.user_id for share in bill_in.shares]
    else:
        participant_ids = [member.id for member in group.members if member.id != payer_id]

    shares = bill_in.shares or []
    defined_shares = {share.user_id: share.amount for share in shares if share.amount}
    defined_amounts = sum(share.amount for share in defined_shares.values())
    default_amount = (bill_in.total_amount - defined_amounts) / (
        len(participant_ids) - len(defined_shares) + 1  # payer
    )

    amounts = {
        participant_id: defined_shares.get(participant_id, default_amount)
        for participant_id in participant_ids
    }
    bill = await repositories.bills.create_bill(
        session,
        repositories.bills.Bill(
            **bill_in.dict(exclude={'payer_id'}), payer_id=payer_id, amounts=amounts
        ),
    )
    await session.commit()
    # await session.refresh(bill)
    return bill


async def get_bill(
    bill_id: int, user: models.User, session: AsyncSession
) -> models.Bill | None:
    bill = await repositories.bills.get_bill(session, bill_id)
    if not bill:
        return None
    if user not in bill.participants and user is not bill.payer:
        raise AuthError(f'User id={user.id} is not a participant of a bill id={bill_id}')
    return bill


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
