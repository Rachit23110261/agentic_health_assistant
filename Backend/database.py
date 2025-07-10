from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

DATABASE_URL = "postgresql://agentic_db_85if_user:VOSG2pTdIuFsNNfPjWFH8Lde7W2R3r3F@dpg-d1nm6eruibrs7387stj0-a/agentic_db_85if"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
@asynccontextmanager
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
