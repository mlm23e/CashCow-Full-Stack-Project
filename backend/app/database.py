import os
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from app.config import settings

DATABASE_URL = settings.database_url

# os.environ.get(
#     "DATABASE_URL",
#     "postgresql+asyncpg://mmarse:password@localhost:5432/cashcow_dev"
# )

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

# expire_on_commit = False 
# this prevents the session from expiring objects after a commit
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)