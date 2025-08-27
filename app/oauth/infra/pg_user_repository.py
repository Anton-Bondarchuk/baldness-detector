from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from app.oauth.domain.models.user import User
from app.oauth.interfaces.dto.user import UserDTO

class PgUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_or_update(self, user_dto: UserDTO) -> User:
        """
        Create a new user if they don't exist, or update an existing one
        based on the email address.
        
        Args:
            user_dto: The user data transfer object
            
        Returns:
            The created or updated user entity
        """
        # Check if user already exists
        query = select(User).where(User.email == user_dto.email)
        result = await self.session.execute(query)
        existing_user = result.scalars().first()
        
        if existing_user:
            # Update existing user
            stmt = (
                update(User)
                .where(User.email == user_dto.email)
                .values(
                    name=user_dto.name,
                    picture=user_dto.picture,
                    google_id=user_dto.google_id
                )
                .returning(User)
            )
            result = await self.session.execute(stmt)
            updated_user = result.scalars().first()
            await self.session.commit()
            return updated_user
        else:
            # Create new user
            new_user = User(
                email=user_dto.email,
                name=user_dto.name,
                picture=user_dto.picture,
                google_id=user_dto.google_id
            )
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user
            
    async def get_by_email(self, email: str) -> User:
        """Get a user by email address"""
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        
        return result.scalars().first()
        
    async def get_by_google_id(self, google_id: str) -> User:
        """Get a user by Google ID"""
        query = select(User).where(User.google_id == google_id)
        result = await self.session.execute(query)
        
        return result.scalars().first()