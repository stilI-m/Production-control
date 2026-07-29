from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from src.core.config import settings

engine = create_async_engine(url=settings.database_url, echo=False, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, )

async def get_async_session():
    async with async_session_maker() as session:
        yield session