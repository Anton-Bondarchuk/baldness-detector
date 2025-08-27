from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.oauth.infra.connection import get_db_session

async def get_db():
    """Dependency for database session"""
    async with get_db_session() as session:
        yield session