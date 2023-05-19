from sqlalchemy.ext.asyncio import AsyncSession

import models
import serializers


async def create_user(session: AsyncSession, user_in: serializers.UserIn) -> models.User:
    user = models.User(name=user_in.name, email=user_in.email, password=user_in.password)
    session.add(user)
    return user
