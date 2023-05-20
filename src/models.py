from typing import Annotated

from sqlalchemy import Float, ForeignKey, Integer, String, MetaData, Table, Column
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import relationship, mapped_column, DeclarativeBase, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

int_pk = Annotated[int, mapped_column(primary_key=True)]
user_fk = Annotated[int, mapped_column(ForeignKey('users.id'))]


# class Base(DeclarativeBase):
#     metadata = metadata


class Base(AsyncAttrs, DeclarativeBase):
    metadata = metadata


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    groups: Mapped[list['Group']] = relationship(
        secondary='memberships', back_populates='members'
    )
    # bills: Mapped[list['Bill']] = relationship(
    #     secondary='bill_shares', back_populates='participants'
    # )


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    members: Mapped[list['User']] = relationship(
        back_populates='groups', secondary='memberships', lazy='joined'
    )
    bills: Mapped[list['Bill']] = relationship(back_populates='group')


memberships = Table(
    'memberships',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('group_id', ForeignKey('groups.id'), primary_key=True),
)


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


class BillShare(Base):
    __tablename__ = 'bill_shares'

    bill_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('bills.id'), primary_key=True
    )
    user_id: Mapped[user_fk] = mapped_column(primary_key=True)

    bill: Mapped['Bill'] = relationship()
    user: Mapped['User'] = relationship(lazy='joined')

    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str | None] = mapped_column(String(255))
    amount: Mapped[float]

    payer_id: Mapped[user_fk] = mapped_column()
    payer: Mapped['User'] = relationship(foreign_keys=payer_id)

    bill_id: Mapped[int] = mapped_column(ForeignKey('bills.id'))
    bill: Mapped['Bill'] = relationship(back_populates='transactions')

    receiver_id: Mapped[user_fk] = mapped_column()
    receiver: Mapped['User'] = relationship(foreign_keys=receiver_id)
