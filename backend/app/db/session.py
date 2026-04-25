"""
Database session and engine configuration for MakanAI.

Sets up the async SQLAlchemy engine and session factory
using asyncpg as the PostgreSQL driver.

Exports:
    engine            → async SQLAlchemy engine instance
    AsyncSessionLocal → async session factory
    Base              → declarative base for all ORM models
    get_db()          → FastAPI dependency for DB sessions
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# ─────────────────────────────────────────────
# Database Engine
# ─────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True if settings.APP_ENV == "development" else False,  # logs SQL queries (for debugging)
    pool_pre_ping=True, # check connection before using it
    pool_size=10, # maintain 10 active connections ready to use
    max_overflow=20 # create up to 20 extra connection
)

# ─────────────────────────────────────────────
# Session Factory
# ───────────────────────────────────────────── 
AsyncSessionLocal = async_sessionmaker (
    engine,  # ore db connecttion interface
    class_=AsyncSession, 
    expire_on_commit=False,  # Data stays usable after saving to db
    autocommit=False,  
    autoflush=False
)

# ─────────────────────────────────────────────
# Base Class
# ─────────────────────────────────────────────
# ALL models must inherit from this Base so
# Alembic can detect them during autogenerate
class Base(DeclarativeBase):
    pass 


# ─────────────────────────────────────────────
# Database Dependency
# ─────────────────────────────────────────────
async def get_db() -> AsyncSession: # type: ignore
    """
    FastAPI dependency that manages the database session lifecycle.

    Yields a database session to the route that needs it.
    Automatically commits on success and rolls back on error.

    Usage in routes:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:  # create async session
        try:
            yield session               # gives data to ur code - API endpoint uses it 
            await session.commit()
        except Exception:
            await session.rollback()    # rollback (undo) if errors 
            raise
        finally:
            await session.close()