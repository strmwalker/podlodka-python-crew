import asyncio

import models
from config import Settings
from db import engine_factory


async def create():
    settings = Settings()
    engine = engine_factory(settings)
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
        # await conn.run_sync(models.Base.metadata.create_all)

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(create())
