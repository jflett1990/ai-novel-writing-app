"""
Story model - represents a single writing project (novel or screenplay).
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class Story(Base):
    """
    Story model representing a single writing project.
    
    This serves as the parent for all related content (characters, plot points, etc.).
    """
    __tablename__ = "stories"
    
    # Primary key
    story_id = Column(Integer, primary_key=True, index=True)
    
    # Future auth support - nullable for now
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, index=True)
    
    # Basic story information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # Synopsis/premise
    genre = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Generation settings (stored as part of story for customization)
    target_word_count = Column(Integer, default=80000)  # Target novel length
    target_chapters = Column(Integer, default=20)
    
    # Relationships
    user = relationship("User", back_populates="stories")
    acts = relationship("Act", back_populates="story", cascade="all, delete-orphan")
    chapters = relationship("Chapter", back_populates="story", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="story", cascade="all, delete-orphan")
    world_elements = relationship("WorldElement", back_populates="story", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Story(id={self.story_id}, title='{self.title}')>"


class Act(Base):
    """
    Act model for story structure (Act I, II, III, etc.).
    Optional grouping for chapters.
    """
    __tablename__ = "acts"
    
    act_id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.story_id"), nullable=False, index=True)
    
    # Act information
    number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    title = Column(String(255), nullable=True)  # e.g., "Act I: Introduction"
    summary = Column(Text, nullable=True)  # Description of what happens in this act
    
    # Relationships
    story = relationship("Story", back_populates="acts")
    chapters = relationship("Chapter", back_populates="act", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Act(id={self.act_id}, number={self.number}, title='{self.title}')>"
