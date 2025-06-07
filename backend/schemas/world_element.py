"""
Pydantic schemas for WorldElement-related API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class WorldElementBase(BaseModel):
    """Base schema for WorldElement."""
    type: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    category: Optional[str] = Field(None, max_length=100)
    importance: Optional[str] = Field(default="medium", pattern="^(high|medium|low)$")


class WorldElementCreate(WorldElementBase):
    """Schema for creating a new world element."""
    pass


class WorldElementUpdate(BaseModel):
    """Schema for updating a world element."""
    type: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    category: Optional[str] = Field(None, max_length=100)
    importance: Optional[str] = Field(None, pattern="^(high|medium|low)$")


class WorldElementResponse(WorldElementBase):
    """Schema for WorldElement response."""
    element_id: int
    story_id: int
    
    class Config:
        from_attributes = True


class WorldElementTypesResponse(BaseModel):
    """Schema for available world element types."""
    types: List[str]


class WorldElementsByTypeResponse(BaseModel):
    """Schema for world elements grouped by type."""
    elements_by_type: Dict[str, List[WorldElementResponse]]
