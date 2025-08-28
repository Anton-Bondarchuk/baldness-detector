from sqlalchemy import Column, Integer, String, DateTime, Identity
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Identity(), primary_key=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    picture = Column(String(1024), nullable=True)
    google_id = Column(String(255), nullable=True, index=True)
    wallet_address = Column(String(255), nullable=True, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"