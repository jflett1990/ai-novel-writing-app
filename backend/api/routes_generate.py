"""
API routes for AI generation functionality.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import json

from db.database import get_db
from models.story import Story
from schemas.story import OutlineGenerateRequest, OutlineResponse
from schemas.character import CharacterGenerateRequest, CharacterGenerateResponse
from services.generation_service import GenerationService

router = APIRouter()


@router.post("/stories/{story_id}/outline", response_model=OutlineResponse)
async def generate_outline(
    story_id: int,
    request: OutlineGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate an outline for a story.
    
    Args:
        story_id: ID of the story
        request: Outline generation parameters
        db: Database session
        
    Returns:
        Generated outline
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Generate outline
    generation_service = GenerationService(db)
    result = await generation_service.generate_outline(
        story_id=story_id,
        target_chapters=request.target_chapters,
        custom_prompt=request.custom_prompt
    )
    
    return result


@router.post("/stories/{story_id}/chapters/{chapter_number}")
async def generate_chapter(
    story_id: int,
    chapter_number: int,
    custom_prompt: Optional[str] = None,
    stream: bool = False,
    db: Session = Depends(get_db)
):
    """
    Generate content for a specific chapter.
    
    Args:
        story_id: ID of the story
        chapter_number: Chapter number to generate
        custom_prompt: Optional custom prompt
        stream: Whether to stream the response
        db: Database session
        
    Returns:
        Generated chapter content (streaming or complete)
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    generation_service = GenerationService(db)
    
    if stream:
        # Return streaming response
        async def generate_stream():
            try:
                result_generator = generation_service.generate_chapter_stream(
                    story_id=story_id,
                    chapter_number=chapter_number,
                    custom_prompt=custom_prompt
                )
                async for chunk in result_generator:
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                error_chunk = {
                    "type": "error",
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    else:
        # Return complete response
        result = await generation_service.generate_chapter(
            story_id=story_id,
            chapter_number=chapter_number,
            custom_prompt=custom_prompt,
            stream=False
        )
        return result


@router.post("/stories/{story_id}/characters", response_model=CharacterGenerateResponse)
async def generate_characters(
    story_id: int,
    request: CharacterGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate characters for a story.

    Args:
        story_id: ID of the story
        request: Character generation parameters
        db: Database session

    Returns:
        Generated characters
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Generate characters
    generation_service = GenerationService(db)
    result = await generation_service.generate_characters(
        story_id=story_id,
        character_count=request.character_count
    )

    return result


@router.post("/stories/{story_id}/world")
async def generate_world_elements(
    story_id: int,
    element_count: int = 8,
    db: Session = Depends(get_db)
):
    """
    Generate world building elements for a story.

    Args:
        story_id: ID of the story
        element_count: Number of world elements to generate
        db: Database session

    Returns:
        Generated world elements
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Generate world elements
    generation_service = GenerationService(db)
    result = await generation_service.generate_world_elements(
        story_id=story_id,
        element_count=element_count
    )

    return result


@router.post("/stories/{story_id}/chapters/{chapter_number}/edit")
async def edit_chapter_content(
    story_id: int,
    chapter_number: int,
    instruction: str,
    paragraph: str,
    db: Session = Depends(get_db)
):
    """
    AI-assisted editing of chapter content.

    Args:
        story_id: ID of the story
        chapter_number: Chapter number
        instruction: Editing instruction (e.g., "make more suspenseful")
        paragraph: Text to edit
        db: Database session

    Returns:
        Edited text
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    generation_service = GenerationService(db)

    try:
        # Use the editing prompt template
        from utils.prompt_templates import PromptTemplates
        prompt_templates = PromptTemplates()

        prompt = prompt_templates.get_editing_prompt(
            original_text=paragraph,
            instruction=instruction,
            context=f"Chapter {chapter_number} of '{story.title}'"
        )

        # Use creative writing parameters for editing
        from services.ai_providers.base import GenerationParams
        params = GenerationParams.for_creative_writing()
        params.max_tokens = 2000

        result = await generation_service.ai_provider.generate_text(prompt, params)

        return {
            "success": True,
            "original_text": paragraph,
            "edited_text": result.text,
            "instruction": instruction,
            "tokens_used": result.tokens_used
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "original_text": paragraph,
            "edited_text": paragraph,
            "instruction": instruction
        }


@router.post("/enhance-sophistication")
async def enhance_text_sophistication(
    text: str,
    focus_area: str = "general",
    db: Session = Depends(get_db)
):
    """
    Enhance text sophistication and originality.

    Args:
        text: Text to enhance
        focus_area: Area to focus on (dialogue, description, pacing, character, general)
        db: Database session

    Returns:
        Enhanced text with improved sophistication
    """
    generation_service = GenerationService(db)

    try:
        from utils.prompt_templates import PromptTemplates
        prompt_templates = PromptTemplates()

        prompt = prompt_templates.get_sophistication_prompt(
            original_text=text,
            focus_area=focus_area
        )

        # Use creative writing parameters for sophistication enhancement
        from services.ai_providers.base import GenerationParams
        params = GenerationParams.for_creative_writing()
        params.max_tokens = len(text.split()) * 2  # Allow for expansion

        result = await generation_service.ai_provider.generate_text(prompt, params)

        return {
            "success": True,
            "original_text": text,
            "enhanced_text": result.text,
            "focus_area": focus_area,
            "tokens_used": result.tokens_used,
            "improvement_notes": f"Enhanced for {focus_area} sophistication"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "original_text": text,
            "enhanced_text": text,
            "focus_area": focus_area
        }


@router.post("/stories/{story_id}/full-draft")
async def generate_full_draft(
    story_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate a complete novel draft (outline + all chapters).
    
    This is a long-running operation that runs in the background.
    
    Args:
        story_id: ID of the story
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Task started confirmation
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    async def generate_full_novel():
        """Background task to generate complete novel."""
        generation_service = GenerationService(db)
        
        # First generate outline
        outline_result = await generation_service.generate_outline(story_id)
        if not outline_result.get("success"):
            return
        
        # Then generate all chapters
        chapters = outline_result.get("outline", {}).get("chapters", [])
        for chapter_data in chapters:
            chapter_number = chapter_data["number"]
            await generation_service.generate_chapter(
                story_id=story_id,
                chapter_number=chapter_number
            )
    
    # Add to background tasks
    background_tasks.add_task(generate_full_novel)
    
    return {
        "message": "Full draft generation started",
        "story_id": story_id,
        "status": "in_progress"
    }


@router.get("/providers")
async def get_ai_providers():
    """
    Get information about available AI providers.
    
    Returns:
        Available AI providers and their capabilities
    """
    from services.ai_providers import get_available_providers
    
    providers = get_available_providers()
    
    # Add current provider status
    from core.config import settings
    current_provider = settings.ai_provider
    
    return {
        "current_provider": current_provider,
        "available_providers": providers
    }


@router.get("/providers/status")
async def check_provider_status():
    """
    Check the status of the current AI provider.

    Returns:
        Provider availability status
    """
    from services.ai_providers import create_ai_provider
    from core.config import settings

    try:
        provider = create_ai_provider()
        is_available = await provider.is_available()
        model_info = provider.get_model_info()

        return {
            "provider": settings.ai_provider,
            "available": is_available,
            "model_info": model_info
        }
    except Exception as e:
        return {
            "provider": settings.ai_provider,
            "available": False,
            "error": str(e)
        }


@router.get("/complexity")
async def get_complexity_setting():
    """
    Get the current novel complexity setting.

    Returns:
        Current complexity level and available options
    """
    from core.config import settings

    return {
        "current_complexity": settings.novel_complexity,
        "available_levels": ["simple", "standard", "complex", "literary"],
        "descriptions": {
            "simple": "Clear, straightforward storytelling with accessible language",
            "standard": "Balanced plot and character development with moderate complexity",
            "complex": "Multi-layered narratives with sophisticated themes and techniques",
            "literary": "Artistic prose with experimental techniques and deep philosophical themes"
        }
    }


@router.post("/complexity/{level}")
async def set_complexity_level(level: str):
    """
    Set the novel complexity level.

    Args:
        level: Complexity level (simple, standard, complex, literary)

    Returns:
        Confirmation of the new setting
    """
    valid_levels = ["simple", "standard", "complex", "literary"]

    if level not in valid_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid complexity level. Must be one of: {', '.join(valid_levels)}"
        )

    # Note: This changes the setting for the current session only
    # To persist changes, you'd need to update the .env file or use a database
    from core.config import settings
    settings.novel_complexity = level

    return {
        "message": f"Complexity level set to '{level}'",
        "new_complexity": level,
        "note": "This setting applies to new generations only"
    }
