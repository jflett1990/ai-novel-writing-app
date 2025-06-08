"""
Enhanced API routes for AI generation functionality.

Updated to use the enhanced generation service for better quality output.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import json

from db.database import get_db
from models.story import Story
from schemas.story import OutlineGenerateRequest, OutlineResponse
from schemas.character import CharacterGenerateRequest, CharacterGenerateResponse
from services.enhanced_generation_service import EnhancedGenerationService
from services.generation_service import GenerationService  # Keep original for fallback
from core.config import settings

router = APIRouter()


@router.post("/stories/{story_id}/outline", response_model=OutlineResponse)
async def generate_outline(
    story_id: int,
    request: OutlineGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate an outline for a story using enhanced prompting.
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Use original generation service for outlines (they're already good)
    generation_service = GenerationService(db)
    result = await generation_service.generate_outline(
        story_id=story_id,
        target_chapters=request.target_chapters,
        custom_prompt=request.custom_prompt
    )
    
    return result


@router.post("/stories/{story_id}/chapters/{chapter_number}")
async def generate_chapter_enhanced(
    story_id: int,
    chapter_number: int,
    custom_prompt: Optional[str] = None,
    target_word_count: int = Query(2500, ge=1500, le=5000, description="Target word count for the chapter"),
    quality_check: bool = Query(True, description="Enable quality assessment and regeneration"),
    stream: bool = False,
    db: Session = Depends(get_db)
):
    """
    Generate chapter content using enhanced prompting and quality controls.
    
    Args:
        story_id: ID of the story
        chapter_number: Chapter number to generate
        custom_prompt: Optional custom prompt override
        target_word_count: Target word count (1500-5000)
        quality_check: Whether to perform quality assessment
        stream: Whether to stream the response
        db: Database session
        
    Returns:
        Generated chapter content with metadata
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    enhanced_service = EnhancedGenerationService(db)
    
    if stream:
        # Return streaming response
        async def generate_stream():
            try:
                async for chunk in enhanced_service.generate_chapter_enhanced(
                    story_id=story_id,
                    chapter_number=chapter_number,
                    custom_prompt=custom_prompt,
                    target_word_count=target_word_count,
                    stream=True,
                    quality_check=quality_check
                ):
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
        result = await enhanced_service.generate_chapter_enhanced(
            story_id=story_id,
            chapter_number=chapter_number,
            custom_prompt=custom_prompt,
            target_word_count=target_word_count,
            stream=False,
            quality_check=quality_check
        )
        return result


@router.post("/stories/{story_id}/chapters/{chapter_number}/multi-pass")
async def generate_chapter_multi_pass(
    story_id: int,
    chapter_number: int,
    target_word_count: int = Query(2500, ge=1500, le=5000),
    db: Session = Depends(get_db)
):
    """
    Generate chapter using multi-pass approach for highest quality.
    
    This method uses three passes:
    1. Structure and plot beats
    2. Character development and dialogue
    3. Prose refinement and expansion
    
    Takes longer but produces higher quality results.
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    enhanced_service = EnhancedGenerationService(db)
    
    result = await enhanced_service.generate_chapter_multi_pass(
        story_id=story_id,
        chapter_number=chapter_number,
        target_word_count=target_word_count
    )
    
    return result


@router.post("/stories/{story_id}/chapters/{chapter_number}/analyze-quality")
async def analyze_chapter_quality(
    story_id: int,
    chapter_number: int,
    db: Session = Depends(get_db)
):
    """
    Analyze the quality of an existing chapter.
    
    Returns quality metrics and improvement suggestions.
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Get the chapter
    from models.chapter import Chapter
    chapter = db.query(Chapter).filter(
        Chapter.story_id == story_id,
        Chapter.number == chapter_number
    ).first()
    
    if not chapter or not chapter.content:
        raise HTTPException(status_code=404, detail="Chapter not found or has no content")
    
    enhanced_service = EnhancedGenerationService(db)
    previous_chapters = enhanced_service._get_previous_chapters(story_id, chapter_number)
    
    quality_score = enhanced_service._assess_content_quality(
        chapter.content, 
        chapter.word_count or 2000, 
        previous_chapters
    )
    
    # Analyze specific issues
    analysis = {
        "quality_score": quality_score,
        "word_count": len(chapter.content.split()),
        "paragraph_count": len([p for p in chapter.content.split('\n\n') if p.strip()]),
        "dialogue_count": chapter.content.count('"'),
        "issues": [],
        "suggestions": []
    }
    
    # Check for specific issues
    content_lower = chapter.content.lower()
    banned_phrases = [
        "little did", "unbeknownst", "time seemed to slow", "heart pounded",
        "blood ran cold", "breath caught", "world spun"
    ]
    
    for phrase in banned_phrases:
        if phrase in content_lower:
            analysis["issues"].append(f"Contains clichéd phrase: '{phrase}'")
            analysis["suggestions"].append(f"Remove or rephrase instances of '{phrase}'")
    
    if analysis["word_count"] < 1500:
        analysis["issues"].append("Chapter is too short")
        analysis["suggestions"].append("Expand with more detailed scenes, dialogue, and description")
    
    if analysis["dialogue_count"] < 4:
        analysis["issues"].append("Insufficient dialogue")
        analysis["suggestions"].append("Add more character conversations and interactions")
    
    if analysis["paragraph_count"] < 6:
        analysis["issues"].append("Too few paragraphs - may lack structure")
        analysis["suggestions"].append("Break content into more distinct scenes and moments")
    
    return analysis


@router.post("/stories/{story_id}/chapters/{chapter_number}/regenerate")
async def regenerate_chapter_with_feedback(
    story_id: int,
    chapter_number: int,
    feedback: str = Query(..., description="Specific feedback on what to improve"),
    target_word_count: int = Query(2500, ge=1500, le=5000),
    db: Session = Depends(get_db)
):
    """
    Regenerate a chapter with specific feedback incorporated.
    
    Args:
        story_id: ID of the story
        chapter_number: Chapter number to regenerate
        feedback: Specific feedback on what to improve
        target_word_count: Target word count for regeneration
    """
    # Verify story exists
    story = db.query(Story).filter(Story.story_id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    enhanced_service = EnhancedGenerationService(db)
    
    # Get existing context
    context = enhanced_service.context_service.get_chapter_context(story_id, chapter_number)
    previous_chapters = enhanced_service._get_previous_chapters(story_id, chapter_number)
    
    # Build enhanced prompt with feedback
    enhanced_prompt = enhanced_service.prompt_templates.get_enhanced_chapter_prompt(
        chapter_info=context["current_chapter"],
        story_context=context,
        previous_chapters=previous_chapters,
        complexity=settings.novel_complexity,
        target_word_count=target_word_count
    )
    
    # Add feedback-specific instructions
    feedback_prompt = f"""{enhanced_prompt}

SPECIFIC IMPROVEMENT REQUIREMENTS BASED ON FEEDBACK:
{feedback}

CRITICAL: Address all feedback points while maintaining the enhanced writing standards above."""
    
    result = await enhanced_service.generate_chapter_enhanced(
        story_id=story_id,
        chapter_number=chapter_number,
        custom_prompt=feedback_prompt,
        target_word_count=target_word_count,
        quality_check=True
    )
    
    return result


# Keep existing endpoints for backwards compatibility
@router.get("/providers")
async def get_ai_providers():
    """Get information about available AI providers."""
    from services.ai_providers import get_available_providers
    
    providers = get_available_providers()
    current_provider = settings.ai_provider
    
    return {
        "current_provider": current_provider,
        "available_providers": providers
    }


@router.get("/providers/status")
async def check_provider_status():
    """Check the status of the current AI provider."""
    from services.ai_providers import create_ai_provider

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
    """Get the current novel complexity setting."""
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
    """Set the novel complexity level."""
    valid_levels = ["simple", "standard", "complex", "literary"]

    if level not in valid_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid complexity level. Must be one of: {', '.join(valid_levels)}"
        )

    # Note: This changes the setting for the current session only
    settings.novel_complexity = level

    return {
        "message": f"Complexity level set to '{level}'",
        "new_complexity": level,
        "note": "This setting applies to new generations only"
    }
