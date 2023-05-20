import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import serializers
import services


async def test_create_user(db_session: AsyncSession):
    user_in = serializers.UserIn(
        name='johndoe', email='johndoe@example.com', password='password'
    )
    user = await services.create_user(user_in, db_session)
    assert user.id == 1


async def test_create_user_raises(db_session: AsyncSession):
    user_in = serializers.UserIn(
        name='johndoe', email='johndoe@example.com', password='password'
    )
    await services.create_user(user_in, db_session)
    with pytest.raises(services.ServiceError):
        await services.create_user(user_in, db_session)
