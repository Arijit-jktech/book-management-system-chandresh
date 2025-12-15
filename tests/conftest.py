import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Use an in-memory SQLite database for testing, or a separate test DB
# For async, we need aiosqlite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(prepare_database) -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
