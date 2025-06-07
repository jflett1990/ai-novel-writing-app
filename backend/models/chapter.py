"""
Chapter model - represents individual chapters within a story.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class Chapter(Base):
    """
    Chapter model storing both outline (summary) and content (actual text).
    
    The separation of summary vs content is helpful:
    - summary: the plan/outline for the chapter
    - content: the actual narrative text
    """
    __tablename__ = "chapters"
    
    # Primary key
    chapter_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    story_id = Column(Integer, ForeignKey("stories.story_id"), nullable=False, index=True)
    act_id = Column(Integer, ForeignKey("acts.act_id"), nullable=True, index=True)  # Optional grouping
    
    # Chapter information
    number = Column(Integer, nullable=False)  # Chapter number within story
    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)  # Outline/plan for this chapter
    content = Column(Text, nullable=True)  # Actual chapter text
    
    # Status tracking
    is_generated = Column(Boolean, default=False)  # Has AI content been generated?
    is_approved = Column(Boolean, default=False)   # Has user approved the content?
    word_count = Column(Integer, default=0)        # Cached word count
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    story = relationship("Story", back_populates="chapters")
    act = relationship("Act", back_populates="chapters")
    revisions = relationship("ChapterRevision", back_populates="chapter", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Chapter(id={self.chapter_id}, number={self.number}, title='{self.title}')>"
    
    def update_word_count(self):
        """Update the cached word count based on current content."""
        if self.content:
            self.word_count = len(self.content.split())
        else:
            self.word_count = 0


class ChapterRevision(Base):
    """
    Chapter revision model for version control.
    Stores historical versions of chapter content.
    """
    __tablename__ = "chapter_revisions"
    
    revision_id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.chapter_id"), nullable=False, index=True)
    
    # Revision data
    revision_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)  # Summary at time of revision
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)  # Optional notes about this revision
    
    # Relationships
    chapter = relationship("Chapter", back_populates="revisions")
    
    def __repr__(self):
        return f"<ChapterRevision(id={self.revision_id}, chapter_id={self.chapter_id}, rev={self.revision_number})>"
