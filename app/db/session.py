from sqlmodel import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from .base import engine
from fastapi import Depends
from .base import AsyncSessionLocal

def get_session():
    with Session(engine) as session:
        yield session

async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
