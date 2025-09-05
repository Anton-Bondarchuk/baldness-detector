


from app.oauth.infra.pg_user_repository import PgUserRepository
from app.oauth.interfaces.dto.user import UserDTO
from app.oauth.domain.models.user import User 


async def _to_dto(user_info) -> UserDTO:
    return UserDTO(
        email=user_info['email'],
        name=user_info['name'],
        picture=user_info['picture'],
        google_id=user_info['sub']
    )

async def _create_or_get_user(user_dto: UserDTO, repo: PgUserRepository) -> User:
        """
        Create a new user or get existing one
        
        Args:
            user_dto: User data transfer object
            
        Returns:
            User entity
        """
        existing_user = await repo.get_by_email(user_dto.email)

        if existing_user:
            return await repo.create_or_update(user_dto)

        if user_dto.google_id:
            existing_user = await repo.get_by_google_id(user_dto.google_id)
            if existing_user:
                return await repo.create_or_update(user_dto)
        
        return await repo.create_or_update(user_dto)