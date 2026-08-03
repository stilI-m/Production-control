import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from sqlalchemy.ext.compiler import compiles
from sqlalchemy import ARRAY

# Импортируем наше приложение и базовые модели/зависимости
from src.main import app
from src.core.dependencies import get_db
from src.data.models import Base

@compiles(ARRAY, "sqlite")
def compile_array_sqlite(element, compiler, **kw):
    return "JSON"
# Используем асинхронную SQLite в памяти для тестов (изолированно и быстро)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
test_async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(autouse=True)
async def setup_database():
    """Автоматически создает все таблицы перед тестом и очищает после."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Подменяем реальную сессию БД на тестовую сессию в памяти."""
    async with test_async_session_maker() as session:
        yield session

# Переопределяем стандартную зависимость get_db на тестовую
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True
    ) as ac:
        yield ac