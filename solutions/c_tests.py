

@pytest.fixture()
async def db_session1(db_connection):
    async with db.Session() as session:
        yield session


@pytest.fixture
async def db_session(db_connection):
    transaction = await db_connection.begin()
    async with db.Session() as session:
        yield session
    await transaction.rollback()

