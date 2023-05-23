from typing import Annotated

from sqlalchemy import ForeignKey, String, MetaData, Table, Column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import relationship, mapped_column, DeclarativeBase, Mapped

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


class Base(AsyncAttrs, DeclarativeBase):
    metadata = metadata


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))

    groups: Mapped[list['Group']] = relationship(
        secondary='memberships', back_populates='members'
    )


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(255))

    members: Mapped[list['User']] = relationship(
        back_populates='groups', secondary='memberships', lazy='joined'
    )


memberships = Table(
    'memberships',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('group_id', ForeignKey('groups.id'), primary_key=True),
)


class Bill(Base):
    __tablename__ = 'bills'

    id: Mapped[int_pk]
    description: Mapped[str] = mapped_column(String(255))
    total_amount: Mapped[float]

    payer_id: Mapped[user_fk]
    payer: Mapped['User'] = relationship(lazy='joined')

    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'))
    group: Mapped['Group'] = relationship()

    shares: Mapped[list['BillShare']] = relationship(lazy='joined', back_populates='bill')

    transactions: Mapped[list['Transaction']] = relationship(back_populates='bill')


class BillShare(Base):
    __tablename__ = 'bill_shares'

    bill_id: Mapped[int] = mapped_column(ForeignKey('bills.id'), primary_key=True)
    user_id: Mapped[user_fk] = mapped_column(primary_key=True)

    bill: Mapped['Bill'] = relationship()
    user: Mapped['User'] = relationship(lazy='joined')

    amount: Mapped[float]


class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[int_pk]
    description: Mapped[str | None] = mapped_column(String(255))
    amount: Mapped[float]

    payer_id: Mapped[user_fk] = mapped_column()
    payer: Mapped['User'] = relationship(foreign_keys=payer_id)

    bill_id: Mapped[int] = mapped_column(ForeignKey('bills.id'))
    bill: Mapped['Bill'] = relationship(back_populates='transactions')

    receiver_id: Mapped[user_fk] = mapped_column()
    receiver: Mapped['User'] = relationship(foreign_keys=receiver_id)
