"""
Pydantic schemas for Story-related API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StoryBase(BaseModel):
    """Base schema for Story."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    genre: Optional[str] = None
    target_word_count: Optional[int] = Field(default=80000, ge=1000, le=500000)
    target_chapters: Optional[int] = Field(default=20, ge=1, le=100)


class StoryCreate(StoryBase):
    """Schema for creating a new story."""
    pass


class StoryUpdate(BaseModel):
    """Schema for updating a story."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    genre: Optional[str] = None
    target_word_count: Optional[int] = Field(None, ge=1000, le=500000)
    target_chapters: Optional[int] = Field(None, ge=1, le=100)


class ActResponse(BaseModel):
    """Schema for Act response."""
    act_id: int
    number: int
    title: Optional[str]
    summary: Optional[str]
    
    class Config:
        from_attributes = True


class ChapterResponse(BaseModel):
    """Schema for Chapter response."""
    chapter_id: int
    number: int
    title: Optional[str]
    summary: Optional[str]
    content: Optional[str]
    is_generated: bool
    is_approved: bool
    word_count: int
    act_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ChapterSummary(BaseModel):
    """Schema for Chapter summary (without content)."""
    chapter_id: int
    number: int
    title: Optional[str]
    summary: Optional[str]
    is_generated: bool
    is_approved: bool
    word_count: int
    act_id: Optional[int]
    
    class Config:
        from_attributes = True


class StoryResponse(StoryBase):
    """Schema for Story response."""
    story_id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StoryDetailResponse(StoryResponse):
    """Schema for detailed Story response with related data."""
    acts: List[ActResponse] = []
    chapters: List[ChapterSummary] = []
    character_count: int = 0
    world_element_count: int = 0
    total_word_count: int = 0
    
    class Config:
        from_attributes = True


class ChapterCreate(BaseModel):
    """Schema for creating a chapter."""
    number: int = Field(..., ge=1)
    title: Optional[str] = None
    summary: Optional[str] = None
    act_id: Optional[int] = None


class ChapterUpdate(BaseModel):
    """Schema for updating a chapter."""
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    is_approved: Optional[bool] = None


class OutlineGenerateRequest(BaseModel):
    """Schema for outline generation request."""
    target_chapters: Optional[int] = Field(None, ge=1, le=100)
    custom_prompt: Optional[str] = None


class OutlineResponse(BaseModel):
    """Schema for outline generation response."""
    success: bool
    outline: Optional[dict] = None
    raw_text: Optional[str] = None
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
