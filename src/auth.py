import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

import models
import repositories
from db import get_session

security = HTTPBasic()


async def get_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> models.User:
    user = await repositories.users.get_by_email(session, credentials.username)
    if user:
        password_correct = secrets.compare_digest(
            user.password.encode('utf-8'), credentials.password.encode('utf-8')
        )
        if password_correct:
            return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Incorrect username or password',
        headers={'WWW-Authenticate': 'Basic'},
    )
