from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
