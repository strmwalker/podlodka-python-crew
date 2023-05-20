from pydantic import BaseModel, Field


class Serializer(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class UserIn(Serializer):
    name: str
    email: str
    password: str


class User(Serializer):
    id: int
    name: str
    email: str


class GroupIn(Serializer):
    name: str
    members: list[int] | None


class Group(Serializer):
    id: int
    name: str
    members: list[User]


class BillShare(Serializer):
    user_id: int
    amount: float | None


class BillIn(Serializer):
    description: str
    total_amount: float

    payer_id: int | None
    group_id: int

    shares: list[BillShare] | None


class Share(Serializer):
    user: User
    # user_id: int
    amount: float


class Bill(Serializer):
    id: int
    description: str
    total_amount: float

    payer: User
    shares: list[Share]


class TransactionIn(Serializer):
    amount: float
    bill_id: int
    description: str | None
    recipient_id: int


class Transaction(Serializer):
    id: int
    amount: float
    description: str | None
    recipient: User
    payer: User
