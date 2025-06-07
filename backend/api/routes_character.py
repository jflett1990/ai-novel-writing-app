"""
API routes for Character management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from models.character import Character
from models.story import Story
from schemas.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse
)

router = APIRouter()


@router.get("/story/{story_id}", response_model=List[CharacterResponse])
async def get_story_characters(
    story_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all characters for a story.
    
    Args:
        story_id: ID of the story
        skip: Number of characters to skip
        limit: Maximum number of characters to return
        db: Database session
        
    Returns:
        List of characters
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    characters = db.query(Character).filter(
        Character.story_id == story_id
    ).offset(skip).limit(limit).all()
    
    return characters


@router.post("/story/{story_id}", response_model=CharacterResponse)
async def create_character(
    story_id: int,
    character: CharacterCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new character for a story.
    
    Args:
        story_id: ID of the story
        character: Character creation data
        db: Database session
        
    Returns:
        Created character
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    db_character = Character(
        story_id=story_id,
        name=character.name,
        role=character.role,
        profile=character.profile,
        traits=character.traits,
        arc=character.arc,
        appearance=character.appearance,
        personality=character.personality,
        background=character.background,
        motivations=character.motivations
    )
    
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific character.
    
    Args:
        character_id: ID of the character
        db: Database session
        
    Returns:
        Character data
    """
    character = db.query(Character).filter(Character.character_id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return character


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: int,
    character_update: CharacterUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a character.
    
    Args:
        character_id: ID of the character
        character_update: Character update data
        db: Database session
        
    Returns:
        Updated character
    """
    character = db.query(Character).filter(Character.character_id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Update fields
    update_data = character_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)
    
    db.commit()
    db.refresh(character)
    return character


@router.delete("/{character_id}")
async def delete_character(
    character_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a character.
    
    Args:
        character_id: ID of the character
        db: Database session
        
    Returns:
        Success message
    """
    character = db.query(Character).filter(Character.character_id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    db.delete(character)
    db.commit()
    return {"message": "Character deleted successfully"}
