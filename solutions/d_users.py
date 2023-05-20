

async def get_by_email(session: AsyncSession, email: str) -> models.User | None:
    query = select(models.User).where(models.User.email == email)
    rows = await session.execute(query)
    return rows.scalar_one_or_none()


async def get_by_id(session: AsyncSession, user_id: int) -> models.User | None:
    return await session.get(models.User, user_id)
