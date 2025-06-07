"""
User model - for future authentication support.

Currently not used but included for future multi-user functionality.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class User(Base):
    """
    User model for future authentication support.
    
    This model is prepared for when multi-user functionality is added.
    Currently, the application operates in single-user mode.
    """
    __tablename__ = "users"
    
    # Primary key
    user_id = Column(Integer, primary_key=True, index=True)
    
    # User credentials
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # User profile
    full_name = Column(String(255), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    stories = relationship("Story", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}')>"
