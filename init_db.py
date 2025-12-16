import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.database.database import Base
from app.config import settings


async def init_db():
    """Initialize database - create all tables"""
    engine = create_async_engine(settings.get_db_url, echo=True)
    
    print("\n[DB INIT] Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("[DB INIT] Tables created successfully!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
