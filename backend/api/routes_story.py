"""
API routes for Story management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from models.story import Story, Act
from models.chapter import Chapter
from models.character import Character
from models.world_element import WorldElement
from schemas.story import (
    StoryCreate, 
    StoryUpdate, 
    StoryResponse, 
    StoryDetailResponse,
    ChapterResponse,
    ChapterCreate,
    ChapterUpdate,
    OutlineGenerateRequest,
    OutlineResponse
)
from services.generation_service import GenerationService

router = APIRouter()


@router.get("/", response_model=List[StoryResponse])
async def list_stories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    List all stories.
    
    Args:
        skip: Number of stories to skip
        limit: Maximum number of stories to return
        db: Database session
        
    Returns:
        List of stories
    """
    stories = db.query(Story).offset(skip).limit(limit).all()
    return stories


@router.post("/", response_model=StoryResponse)
async def create_story(
    story: StoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new story.
    
    Args:
        story: Story creation data
        db: Database session
        
    Returns:
        Created story
    """
    db_story = Story(
        title=story.title,
        description=story.description,
        genre=story.genre,
        target_word_count=story.target_word_count,
        target_chapters=story.target_chapters
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story


@router.get("/{story_id}", response_model=StoryDetailResponse)
async def get_story(
    story_id: int,
    include_content: bool = Query(False, description="Include chapter content"),
    db: Session = Depends(get_db)
):
    """
    Get a specific story with details.
    
    Args:
        story_id: ID of the story
        include_content: Whether to include full chapter content
        db: Database session
        
    Returns:
        Story with related data
    """
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Get related data
    acts = db.query(Act).filter(Act.story_id == story_id).order_by(Act.number).all()
    chapters = db.query(Chapter).filter(Chapter.story_id == story_id).order_by(Chapter.number).all()
    character_count = db.query(Character).filter(Character.story_id == story_id).count()
    world_element_count = db.query(WorldElement).filter(WorldElement.story_id == story_id).count()
    
    # Calculate total word count
    total_word_count = sum(ch.word_count for ch in chapters if ch.word_count)
    
    # Prepare response
    response_data = {
        **story.__dict__,
        "acts": acts,
        "chapters": chapters,
        "character_count": character_count,
        "world_element_count": world_element_count,
        "total_word_count": total_word_count
    }
    
    return response_data


@router.put("/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: int,
    story_update: StoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a story.
    
    Args:
        story_id: ID of the story
        story_update: Story update data
        db: Database session
        
    Returns:
        Updated story
    """
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Update fields
    update_data = story_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(story, field, value)
    
    db.commit()
    db.refresh(story)
    return story


@router.delete("/{story_id}")
async def delete_story(
    story_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a story and all related data.
    
    Args:
        story_id: ID of the story
        db: Database session
        
    Returns:
        Success message
    """
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    db.delete(story)
    db.commit()
    return {"message": "Story deleted successfully"}


@router.get("/{story_id}/chapters", response_model=List[ChapterResponse])
async def get_story_chapters(
    story_id: int,
    include_content: bool = Query(True, description="Include chapter content"),
    db: Session = Depends(get_db)
):
    """
    Get all chapters for a story.
    
    Args:
        story_id: ID of the story
        include_content: Whether to include chapter content
        db: Database session
        
    Returns:
        List of chapters
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    chapters = db.query(Chapter).filter(Chapter.story_id == story_id).order_by(Chapter.number).all()
    
    if not include_content:
        # Remove content from response
        for chapter in chapters:
            chapter.content = None
    
    return chapters


@router.get("/{story_id}/chapters/{chapter_number}", response_model=ChapterResponse)
async def get_chapter(
    story_id: int,
    chapter_number: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific chapter.
    
    Args:
        story_id: ID of the story
        chapter_number: Chapter number
        db: Database session
        
    Returns:
        Chapter data
    """
    chapter = db.query(Chapter).filter(
        Chapter.story_id == story_id,
        Chapter.number == chapter_number
    ).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return chapter


@router.put("/{story_id}/chapters/{chapter_number}", response_model=ChapterResponse)
async def update_chapter(
    story_id: int,
    chapter_number: int,
    chapter_update: ChapterUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a chapter.
    
    Args:
        story_id: ID of the story
        chapter_number: Chapter number
        chapter_update: Chapter update data
        db: Database session
        
    Returns:
        Updated chapter
    """
    chapter = db.query(Chapter).filter(
        Chapter.story_id == story_id,
        Chapter.number == chapter_number
    ).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    # Update fields
    update_data = chapter_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chapter, field, value)
    
    # Update word count if content was changed
    if "content" in update_data:
        chapter.update_word_count()
    
    db.commit()
    db.refresh(chapter)
    return chapter
