def repositories_create_user(
    session: AsyncSession, user_in: serializers.UserIn
) -> models.User:
    user = models.User(name=user_in.name, email=user_in.email, password=user_in.password)
    session.add(user)
    return user


async def create_user(user_in: serializers.UserIn, session: AsyncSession) -> models.User:
    user = await repositories.users.create_user(session, user_in)
    try:
        await session.commit()
    except IntegrityError:
        raise ServiceError('User already exists')
    return user


async def get_by_id(session: AsyncSession, user_id: int) -> models.User | None:
    return await session.get(models.User, user_id)


async def get_by_email(session: AsyncSession, email: str) -> models.User | None:
    query = select(models.User).where(models.User.email == email)
    rows = await session.execute(query)
    return rows.scalar_one_or_none()


async def get_by_ids(session: AsyncSession, user_ids: list[int]) -> list[models.User]:
    statement = select(models.User).where(models.User.id.in_(user_ids))
    scalars = await session.scalars(statement)
    return scalars.all()
