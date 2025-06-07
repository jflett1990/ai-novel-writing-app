"""
Character model - represents characters within a story.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from db.database import Base


class Character(Base):
    """
    Character model storing character profiles and arcs.
    
    This table holds the "bible" for each character, providing context
    for AI generation to maintain consistency.
    """
    __tablename__ = "characters"
    
    # Primary key
    character_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    story_id = Column(Integer, ForeignKey("stories.story_id"), nullable=False, index=True)
    
    # Basic character information
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=True)  # e.g., "protagonist", "antagonist", "supporting"
    
    # Character details
    profile = Column(Text, nullable=True)  # Free text description/backstory
    traits = Column(JSON, nullable=True)   # Structured traits: {"age": 30, "occupation": "wizard", ...}
    arc = Column(Text, nullable=True)      # Character's journey/development throughout story
    
    # Physical description
    appearance = Column(Text, nullable=True)
    
    # Personality and background
    personality = Column(Text, nullable=True)
    background = Column(Text, nullable=True)
    motivations = Column(Text, nullable=True)
    
    # Relationships
    story = relationship("Story", back_populates="characters")
    
    def __repr__(self):
        return f"<Character(id={self.character_id}, name='{self.name}', role='{self.role}')>"
    
    def get_context_summary(self) -> str:
        """
        Generate a concise summary of this character for AI context injection.
        
        Returns:
            str: A formatted summary suitable for including in AI prompts
        """
        summary_parts = [f"Character: {self.name}"]
        
        if self.role:
            summary_parts.append(f"Role: {self.role}")
        
        if self.traits and isinstance(self.traits, dict):
            traits_str = ", ".join([f"{k}: {v}" for k, v in self.traits.items()])
            summary_parts.append(f"Traits: {traits_str}")
        
        if self.personality:
            summary_parts.append(f"Personality: {self.personality}")
        
        if self.motivations:
            summary_parts.append(f"Motivations: {self.motivations}")
        
        if self.arc:
            summary_parts.append(f"Character Arc: {self.arc}")
        
        return "\n".join(summary_parts)
