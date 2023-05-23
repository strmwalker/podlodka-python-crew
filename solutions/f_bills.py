async def create_bill0(
    bill_in: serializers.BillIn, user: models.User, session: AsyncSession
) -> models.Bill:
    """Create bill with group and amount"""
    group = await get_group(bill_in.group_id, user, session)

    amount = bill_in.total_amount / len(group.members)

    bill = models.Bill(
        description=bill_in.description,
        total_amount=bill_in.total_amount,
        payer=user,
        group=group,
    )
    for member in group.members:
        if member is user:
            continue
        share = models.BillShare(user=member, amount=amount)
        session.add(share)
        bill.shares.append(share)

    session.add(bill)
    await session.commit()
    return bill


async def create_bill1(
    bill_in: serializers.BillIn, user: models.User, session: AsyncSession
) -> models.Bill:
    """support payer_id"""
    group = await get_group(bill_in.group_id, user, session)

    if bill_in.payer_id:
        payer = await repositories.users.get_by_id(session, bill_in.payer_id)
    else:
        payer = user

    participants = [member for member in group.members if member is not payer]
    amount = bill_in.total_amount / len(group.members)

    bill = models.Bill(
        description=bill_in.description,
        total_amount=bill_in.total_amount,
        payer=payer,
        group=group,
    )
    for participant in participants:
        share = models.BillShare(user=participant, amount=amount)
        session.add(share)
        bill.shares.append(share)

    session.add(bill)
    await session.commit()
    return bill


async def create_bill2(
    bill_in: serializers.BillIn, user: models.User, session: AsyncSession
) -> models.Bill:
    """support participants"""
    group = await get_group(bill_in.group_id, user, session)

    if bill_in.payer_id:
        payer = await repositories.users.get_by_id(session, bill_in.payer_id)
    else:
        payer = user

    shares = bill_in.shares or []
    if shares:
        participants = await repositories.users.get_by_ids(
            session, [s.user_id for s in shares]
        )
    else:
        participants = [member for member in group.members if member is not payer]

    amount = bill_in.total_amount / (len(participants) + 1)

    bill = models.Bill(
        description=bill_in.description,
        total_amount=bill_in.total_amount,
        payer=payer,
        group=group,
    )
    for participant in participants:
        share = models.BillShare(user=participant, amount=amount)
        session.add(share)
        bill.shares.append(share)

    session.add(bill)
    await session.commit()
    return bill


async def create_bill3(
    bill_in: serializers.BillIn, user: models.User, session: AsyncSession
) -> models.Bill:
    """Support custom amounts"""
    group = await get_group(bill_in.group_id, user, session)

    if bill_in.payer_id:
        payer = await repositories.users.get_by_id(session, bill_in.payer_id)
    else:
        payer = user

    shares = bill_in.shares or []
    if shares:
        participants = await repositories.users.get_by_ids(
            session, [s.user_id for s in shares]
        )
    else:
        participants = [member for member in group.members if member is not payer]


    shares = bill_in.shares or []
    defined_shares = {share.user_id: share.amount for share in shares if share.amount}
    defined_amounts = sum(share.amount for share in defined_shares.values())
    default_amount = (bill_in.total_amount - defined_amounts) / (
        len(participant_ids) - len(defined_shares) + 1  # payer
    )

    bill = models.Bill(
        description=bill_in.description,
        total_amount=bill_in.total_amount,
        payer=payer,
        group=group,
    )
    for participant in participants:
        share = models.BillShare(user=participant, amount=defined_shares.get(participant.id, default_amount))
        session.add(share)
        bill.shares.append(share)

    session.add(bill)
    await session.commit()
    return bill


async def create_bill4(
    bill_in: serializers.BillIn, user: models.User, session: AsyncSession
) -> models.Bill:
    """
    Version 1: All group members are participating in bill, current user is payer
    """
    group = await get_group(bill_in.group_id, user, session)

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
    bill_dto = repositories.bills.Bill(
        **bill_in.dict(exclude={'shares', 'payer_id'}), payer_id=user.id, shares=amounts
    )
    bill = repositories.bills.create_bill(session, bill_dto)
    await session.commit()
    await session.refresh(bill)  # required to populate BillShare.user
    return bill


class Bill(Base):
    __tablename__ = 'bills'

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(255))
    total_amount: Mapped[float]

    payer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    payer: Mapped['User'] = relationship(lazy='joined')

    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'))
    group: Mapped['Group'] = relationship(back_populates='bills')

    shares: Mapped[list['BillShare']] = relationship(lazy='joined', back_populates='bill')
    participants: AssociationProxy[list['User']] = association_proxy('shares', 'user')

    transactions: Mapped[list['Transaction']] = relationship(back_populates='bill')


async def get_bill(
    bill_id: int, user: models.User, session: AsyncSession
) -> models.Bill | None:
    bill = await repositories.bills.get_bill(session, bill_id)
    if not bill:
        return None
    if user not in bill.participants and user is not bill.payer:
        raise AuthError(f'User id={user.id} is not a participant of a bill id={bill_id}')
    return bill
