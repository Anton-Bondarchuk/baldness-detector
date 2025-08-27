from abc import ABC, abstractmethod


class UserRepositoryPort(ABC):
    
    @abstractmethod
    def create_or_update(self, user_dto) -> User:
        pass
    
    
    @abstractmethod
    def get_user_by_username(self, username: str):
        pass

    @abstractmethod
    def create_user(self, username: str, password: str):
        pass