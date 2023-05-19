import logging
import uuid

from asyncpg import Connection
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import Settings

logger = logging.getLogger(__name__)


class SQLAlchemyConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f'__asyncpg_{prefix}_{uuid.uuid4()}__'


def engine_factory(settings: Settings):
    return create_async_engine(
        settings.db_dsn(),
        echo=True,
        connect_args={
            'statement_cache_size': 0,
            'prepared_statement_cache_size': 0,
            'connection_class': SQLAlchemyConnection,
        },
        pool_pre_ping=True,
    )


Session = async_sessionmaker(
    # expire_on_commit=False
)


async def get_session():
    async with Session() as session:
        logger.info('Session started')
        yield session
    logger.info('Session closed')
