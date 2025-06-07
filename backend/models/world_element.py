"""
WorldElement model - represents worldbuilding elements within a story.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from db.database import Base


class WorldElement(Base):
    """
    WorldElement model for storing worldbuilding information.
    
    Uses a single table with type discriminator for flexibility.
    Can represent locations, factions, objects, creatures, magic systems, etc.
    """
    __tablename__ = "world_elements"
    
    # Primary key
    element_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    story_id = Column(Integer, ForeignKey("stories.story_id"), nullable=False, index=True)
    
    # Element classification
    type = Column(String(100), nullable=False, index=True)  # 'location', 'faction', 'item', etc.
    name = Column(String(255), nullable=False)
    
    # Element details
    description = Column(Text, nullable=True)  # Main description of this element
    meta = Column(JSON, nullable=True)         # Additional structured info
    
    # Optional categorization
    category = Column(String(100), nullable=True)  # Sub-category within type
    importance = Column(String(50), default="medium")  # "high", "medium", "low" - for context prioritization
    
    # Relationships
    story = relationship("Story", back_populates="world_elements")
    
    def __repr__(self):
        return f"<WorldElement(id={self.element_id}, type='{self.type}', name='{self.name}')>"
    
    def get_context_summary(self) -> str:
        """
        Generate a concise summary of this world element for AI context injection.
        
        Returns:
            str: A formatted summary suitable for including in AI prompts
        """
        summary_parts = [f"{self.type.title()}: {self.name}"]
        
        if self.category:
            summary_parts.append(f"Category: {self.category}")
        
        if self.description:
            # Truncate long descriptions for context
            desc = self.description[:200] + "..." if len(self.description) > 200 else self.description
            summary_parts.append(f"Description: {desc}")
        
        if self.meta and isinstance(self.meta, dict):
            # Include key metadata
            meta_str = ", ".join([f"{k}: {v}" for k, v in self.meta.items() if k in ['ruler', 'population', 'climate', 'power', 'material']])
            if meta_str:
                summary_parts.append(f"Details: {meta_str}")
        
        return "\n".join(summary_parts)
    
    @classmethod
    def get_common_types(cls):
        """
        Return common world element types for UI dropdowns.
        
        Returns:
            list: List of common world element types
        """
        return [
            "location",
            "faction", 
            "organization",
            "item",
            "artifact",
            "creature",
            "species",
            "magic_system",
            "technology",
            "religion",
            "culture",
            "history",
            "event",
            "concept"
        ]
