"""Request models shared by standard and enhanced generation routes."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChapterGenerateRequest(BaseModel):
    custom_prompt: Optional[str] = None


class ChapterExpandRequest(BaseModel):
    expansion_type: Literal["enhance", "lengthen", "detail", "prose"] = "enhance"
    custom_prompt: Optional[str] = None
    target_length: Optional[int] = Field(default=None, ge=250, le=10000)


class EnhancedChapterGenerateRequest(BaseModel):
    custom_prompt: Optional[str] = None
    target_word_count: int = Field(default=2500, ge=1500, le=5000)
    quality_check: bool = True


class MultiPassGenerateRequest(BaseModel):
    target_word_count: int = Field(default=2500, ge=1500, le=5000)


class RegenerateChapterRequest(BaseModel):
    feedback: str = Field(..., min_length=1, max_length=10000)
    target_word_count: int = Field(default=2500, ge=1500, le=5000)
