"""
API routes for WorldElement management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from models.world_element import WorldElement
from models.story import Story
from schemas.world_element import (
    WorldElementCreate,
    WorldElementUpdate,
    WorldElementResponse,
    WorldElementTypesResponse,
    WorldElementsByTypeResponse
)

router = APIRouter()


@router.get("/story/{story_id}", response_model=List[WorldElementResponse])
async def get_story_world_elements(
    story_id: int,
    element_type: Optional[str] = Query(None, description="Filter by element type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all world elements for a story.
    
    Args:
        story_id: ID of the story
        element_type: Optional filter by element type
        skip: Number of elements to skip
        limit: Maximum number of elements to return
        db: Database session
        
    Returns:
        List of world elements
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    query = db.query(WorldElement).filter(WorldElement.story_id == story_id)
    
    if element_type:
        query = query.filter(WorldElement.type == element_type)
    
    elements = query.offset(skip).limit(limit).all()
    return elements


@router.get("/story/{story_id}/by-type", response_model=WorldElementsByTypeResponse)
async def get_story_world_elements_by_type(
    story_id: int,
    db: Session = Depends(get_db)
):
    """
    Get world elements for a story grouped by type.
    
    Args:
        story_id: ID of the story
        db: Database session
        
    Returns:
        World elements grouped by type
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    elements = db.query(WorldElement).filter(WorldElement.story_id == story_id).all()
    
    # Group by type
    elements_by_type = {}
    for element in elements:
        if element.type not in elements_by_type:
            elements_by_type[element.type] = []
        elements_by_type[element.type].append(element)
    
    return {"elements_by_type": elements_by_type}


@router.post("/story/{story_id}", response_model=WorldElementResponse)
async def create_world_element(
    story_id: int,
    element: WorldElementCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new world element for a story.
    
    Args:
        story_id: ID of the story
        element: World element creation data
        db: Database session
        
    Returns:
        Created world element
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    db_element = WorldElement(
        story_id=story_id,
        type=element.type,
        name=element.name,
        description=element.description,
        meta=element.meta,
        category=element.category,
        importance=element.importance
    )
    
    db.add(db_element)
    db.commit()
    db.refresh(db_element)
    return db_element


@router.get("/{element_id}", response_model=WorldElementResponse)
async def get_world_element(
    element_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific world element.
    
    Args:
        element_id: ID of the world element
        db: Database session
        
    Returns:
        World element data
    """
    element = db.query(WorldElement).filter(WorldElement.element_id == element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="World element not found")
    
    return element


@router.put("/{element_id}", response_model=WorldElementResponse)
async def update_world_element(
    element_id: int,
    element_update: WorldElementUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a world element.
    
    Args:
        element_id: ID of the world element
        element_update: World element update data
        db: Database session
        
    Returns:
        Updated world element
    """
    element = db.query(WorldElement).filter(WorldElement.element_id == element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="World element not found")
    
    # Update fields
    update_data = element_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(element, field, value)
    
    db.commit()
    db.refresh(element)
    return element


@router.delete("/{element_id}")
async def delete_world_element(
    element_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a world element.
    
    Args:
        element_id: ID of the world element
        db: Database session
        
    Returns:
        Success message
    """
    element = db.query(WorldElement).filter(WorldElement.element_id == element_id).first()
    if not element:
        raise HTTPException(status_code=404, detail="World element not found")
    
    db.delete(element)
    db.commit()
    return {"message": "World element deleted successfully"}


@router.get("/types", response_model=WorldElementTypesResponse)
async def get_world_element_types():
    """
    Get available world element types.
    
    Returns:
        List of available world element types
    """
    types = WorldElement.get_common_types()
    return {"types": types}
