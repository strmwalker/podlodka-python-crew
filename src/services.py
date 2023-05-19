import logging
from typing import Sequence, Collection

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
    user = await repositories.users.create_user(session, user_in)
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
    await session.refresh(group)
    return group


# async def create_group(
#     name: str, user: models.User, member_ids: list[int] | None, session: AsyncSession
# ):
#     group = await repositories.groups.create_group(session, name, member_ids)
#     # if member_ids:
#     #     members = await repositories.users.get_by_ids(session, member_ids)
#     #     for member in members:
#     #         session.add(models.Membership(user_id=member.id, group_id=group.id))
#     # session.add(models.Membership(user_id=user.id, group=group))
#     group.members.append(user)
#     await session.commit()
#     await session.refresh(group)
#     return group


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


async def get_group(group_id: int, user: models.User, session: AsyncSession) -> models.Group | None:
    group = await repositories.groups.get_by_id(session, group_id)
    if not group:
        return None
    if user not in group.members:
        raise AuthError(f'User id={user.id} is not a member of group id={group.id}')
    return group


async def user_is_participant(user_id: int, bill_id: int, session: AsyncSession) -> bool:
    participant = await repositories.bills.get_participant(session, bill_id, user_id)
    return bool(participant)


async def create_bill(
    bill_in: serializers.BillIn, user: models.User, session: AsyncSession
) -> models.Bill:
    logger.debug('Testing current user group membership')
    group = await repositories.groups.get_by_id(session, bill_in.group_id)
    if user not in group.members:
        raise AuthError(
            f'User id={user.id} is not a member of a group id={bill_in.group_id}'
        )

    logger.debug('Saving bill')
    payer = (
        await repositories.users.get_by_id(session, bill_in.payer_id)
        if bill_in.payer_id
        else user
    )
    group = await repositories.groups.get_by_id(session, bill_in.group_id)
    bill = models.Bill(
        description=bill_in.name,
        total_amount=bill_in.total_amount,
        payer_id=payer.id,
        group_id=group.id,
    )
    session.add(bill)

    logger.debug('Adding bill participants')
    if bill_in.participants:
        participants = bill_in.participants
    else:
        participants = []
        for member in group.members:
            if member.id != payer.id:
                participants.append(serializers.Participant(user_id=member.id))
    amounts = split(bill.total_amount, participants)
    for participant in participants:
        logger.debug('Add participant to bill')
        session.add(
            models.BillShare(
                bill=bill,
                user_id=participant.user_id,
                amount_owed=amounts[participant.user_id],
            )
        )

    logger.debug('Saving participants')
    await session.commit()
    logger.debug('Refreshing bill')
    await session.refresh(bill)
    return bill


async def get_bill(
    bill_id: int, user: models.User, session: AsyncSession
) -> models.Bill | None:
    bill = await repositories.bills.get_bill(session, bill_id)
    if not bill:
        return None
    if user not in bill.participants or user.id != bill.payer_id:
        raise AuthError(f'User id={user.id} is not a participant of a bill id={bill_id}')
    return bill


async def get_amount_owed(bill_id: int, user: models.User, session: AsyncSession):
    share = await repositories.bills.get_participant(session, bill_id, user.id)
    paid_amount = await repositories.transactions.get_paid_transactions(
        session, bill_id, user.id
    )
    return share.amount_owed - paid_amount


async def create_transaction(
    transaction_in: serializers.TransactionIn, user: models.User, session: AsyncSession
):
    is_participant = await user_is_participant(
        transaction_in.recipient_id, transaction_in.bill_id, session
    )
    if not is_participant:
        raise ServiceError(
            f'Recipient is not participant of bill id={transaction_in.bill_id}'
        )
    transaction = await repositories.transactions.add_transaction(
        session, transaction_in, user
    )
    await session.commit()
    return transaction


def split(
    total_amount, participants: Collection[serializers.Participant]
) -> dict[int, float]:
    amounts = {
        participant.user_id: participant.amount
        for participant in participants
        if participant.amount is not None
    }
    prepared = sum(amounts.values())
    equal_shares = len(participants) - len(amounts) + 1
    share = (total_amount - prepared) / equal_shares
    for participant in participants:
        if participant.user_id in amounts:
            continue
        amounts[participant.user_id] = share
    return amounts
