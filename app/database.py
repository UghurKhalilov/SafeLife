from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,           # SQL logları üçün
    pool_pre_ping=True,              # Bağlantı yoxlaması
    pool_size=10,                    # Connection pool
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,          # Commit sonra obyektlər usable qalır
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)