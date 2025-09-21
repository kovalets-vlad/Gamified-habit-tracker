from sqlmodel import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
# For async
sqlite_async_url = f"sqlite+aiosqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

async_engine = create_async_engine(sqlite_async_url, echo=True) 

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
