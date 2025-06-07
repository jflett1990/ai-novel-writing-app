"""
Pydantic schemas for Character-related API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class CharacterBase(BaseModel):
    """Base schema for Character."""
    name: str = Field(..., min_length=1, max_length=255)
    role: Optional[str] = Field(None, max_length=100)
    profile: Optional[str] = None
    traits: Optional[Dict[str, Any]] = None
    arc: Optional[str] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    motivations: Optional[str] = None


class CharacterCreate(CharacterBase):
    """Schema for creating a new character."""
    pass


class CharacterUpdate(BaseModel):
    """Schema for updating a character."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = Field(None, max_length=100)
    profile: Optional[str] = None
    traits: Optional[Dict[str, Any]] = None
    arc: Optional[str] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    motivations: Optional[str] = None


class CharacterResponse(CharacterBase):
    """Schema for Character response."""
    character_id: int
    story_id: int
    
    class Config:
        from_attributes = True


class CharacterGenerateRequest(BaseModel):
    """Schema for character generation request."""
    character_count: Optional[int] = Field(default=5, ge=1, le=20)
    custom_prompt: Optional[str] = None


class CharacterGenerateResponse(BaseModel):
    """Schema for character generation response."""
    success: bool
    characters: Optional[list] = None
    tokens_used: Optional[int] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
