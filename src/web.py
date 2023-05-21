import logging
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, templating, Query, Body
from fastapi.exception_handlers import http_exception_handler
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import auth
import db
import models
import repositories
import serializers
import services
from config import Settings

app = FastAPI()

logger = logging.getLogger(__name__)

settings = Settings()

engine = db.engine_factory(settings)
db.Session.configure(bind=engine)


@app.exception_handler(services.AuthError)
async def error_middleware(request, exc: services.AuthError):
    return await http_exception_handler(
        request, HTTPException(HTTPStatus.FORBIDDEN, detail=str(exc))
    )


@app.exception_handler(services.ServiceError)
async def service_error_middleware(request, exc: services.ServiceError):
    return await http_exception_handler(
        request, HTTPException(HTTPStatus.BAD_REQUEST, detail=str(exc))
    )


@app.exception_handler(services.NotFoundError)
async def not_found_middleware(request, exc: services.NotFoundError):
    return await http_exception_handler(
        request, HTTPException(HTTPStatus.NOT_FOUND, detail=str(exc))
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await engine.connect()
    yield
    await engine.dispose()


@app.get("/")
async def hello():
    return {"Hello": "World"}


@app.get('/db')
async def run_select(session: Annotated[AsyncSession, Depends(db.get_session)]):
    await session.execute(text('select 1'))


@app.get('/users')
async def get_users(
    user_ids: Annotated[list[int], Query()],
    session: Annotated[AsyncSession, Depends(db.get_session)],
):
    users = await repositories.users.get_by_ids(session, user_ids)
    return [serializers.User.from_orm(user) for user in users]


@app.post('/users')
async def create_user(
    user_in: serializers.UserIn, session: Annotated[AsyncSession, Depends(db.get_session)]
) -> serializers.User:
    user = await services.create_user(user_in, session)
    return serializers.User.from_orm(user)


@app.get('/users/me')
async def me(user: Annotated[models.User, Depends(auth.get_user)]):
    return serializers.User.from_orm(user)


@app.get('/users/{user_id}')
async def get_user(
    user_id: int, session: Annotated[AsyncSession, Depends(db.get_session)]
) -> serializers.User:
    user = await repositories.users.get_by_id(session, user_id)
    if user is None:
        raise HTTPException(404, f'User {user_id=} not found')
    return serializers.User.from_orm(user)


@app.post('/groups')
async def create_group(
    group_in: serializers.GroupIn,
    user: Annotated[models.User, Depends(auth.get_user)],
    session: Annotated[AsyncSession, Depends(db.get_session)],
):
    group = await services.create_group(group_in, user, session)
    return serializers.Group.from_orm(group)


@app.get('/groups/{group_id}')
async def get_group(
    group_id: int,
    user: Annotated[models.User, Depends(auth.get_user)],
    session: Annotated[AsyncSession, Depends(db.get_session)],
):
    group = await services.get_group(group_id, user, session)
    return serializers.Group.from_orm(group)


@app.post('/groups/{group_id}/members')
async def add_member(
    user_id: Annotated[int, Body()],
    group_id: int,
    session: Annotated[AsyncSession, Depends(db.get_session)],
):
    group = await services.add_member(user_id, group_id, session)
    return serializers.Group.from_orm(group)


@app.post('/bills')
async def create_bill(
    bill_in: serializers.BillIn,
    user: Annotated[models.User, Depends(auth.get_user)],
    session: Annotated[AsyncSession, Depends(db.get_session)],
):
    """
    Share total amount of bill between group participants.
    If payer_id is not supplied, current user is considered payer
    If amounts are not supplied total amount is divided equally between participants
    """
    bill = await services.create_bill(bill_in, user, session)
    return serializers.Bill.from_orm(bill)


@app.get('/bills/{bill_id}')
async def get_bill(
    bill_id: int,
    user: Annotated[models.User, Depends(auth.get_user)],
    session: Annotated[AsyncSession, Depends(db.get_session)],
):
    bill = await services.get_bill(bill_id, user, session)
    if not bill:
        raise HTTPException(404, f'Bill id={bill_id} not found')
    return serializers.Bill.from_orm(bill)


@app.post('/transactions')
async def create_transaction(
    transaction_in: serializers.TransactionIn,
    user: Annotated[models.User, Depends(auth.get_user)],
    session: Annotated[AsyncSession, Depends(db.get_session)],
):
    await services.create_transaction(transaction_in, user, session)
