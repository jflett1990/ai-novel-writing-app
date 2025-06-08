"""
Enhanced Generation Service with improved prompting and multi-pass generation.

This service implements sophisticated generation strategies to produce longer,
more original content that avoids common AI writing patterns.
"""
import re
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from sqlalchemy.orm import Session

from models.story import Story, Act
from models.character import Character
from models.world_element import WorldElement
from models.chapter import Chapter, ChapterRevision
from services.ai_providers import create_ai_provider
from services.ai_providers.base import GenerationParams, AIProviderError
from services.context_service import ContextService
from utils.enhanced_prompt_templates import EnhancedPromptTemplates
from core.config import settings


class EnhancedGenerationService:
    """
    Advanced generation service with sophisticated prompting and quality controls.
    """
    
    def __init__(self, db: Session):
        """Initialize the enhanced generation service."""
        self.db = db
        self.ai_provider = create_ai_provider()
        self.context_service = ContextService(db)
        self.prompt_templates = EnhancedPromptTemplates()
        self.quality_threshold = 0.7  # Minimum quality score to accept
        self.max_regeneration_attempts = 3
    
    async def generate_chapter_enhanced(
        self,
        story_id: int,
        chapter_number: int,
        custom_prompt: Optional[str] = None,
        target_word_count: int = 2500,
        stream: bool = False,
        quality_check: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a chapter using enhanced prompting with quality controls.
        
        Args:
            story_id: ID of the story
            chapter_number: Chapter number to generate
            custom_prompt: Optional custom prompt override
            target_word_count: Target word count for the chapter
            stream: Whether to return streaming response
            quality_check: Whether to perform quality assessment
            
        Returns:
            Dict containing generated content and metadata
        """
        # Get comprehensive context
        context = self.context_service.get_chapter_context(story_id, chapter_number)
        
        if not context.get("current_chapter"):
            raise ValueError(f"Chapter {chapter_number} not found in story outline")
        
        # Get previous chapters for continuity
        previous_chapters = self._get_previous_chapters(story_id, chapter_number)
        
        for attempt in range(self.max_regeneration_attempts):
            try:
                if custom_prompt:
                    prompt = custom_prompt
                else:
                    # Use enhanced prompt templates
                    prompt = self.prompt_templates.get_enhanced_chapter_prompt(
                        chapter_info=context["current_chapter"],
                        story_context=context,
                        previous_chapters=previous_chapters,
                        complexity=settings.novel_complexity,
                        target_word_count=target_word_count
                    )
                
                # Enhanced generation parameters
                params = self._get_enhanced_generation_params(target_word_count)
                
                if stream:
                    return await self._generate_chapter_stream_enhanced(
                        story_id, chapter_number, prompt, params, target_word_count
                    )
                else:
                    result = await self.ai_provider.generate_text(prompt, params)
                    
                    # Quality assessment
                    if quality_check:
                        quality_score = self._assess_content_quality(
                            result.text, target_word_count, previous_chapters
                        )
                        
                        if quality_score < self.quality_threshold and attempt < self.max_regeneration_attempts - 1:
                            # Regenerate with adjusted prompt
                            prompt = self._adjust_prompt_for_quality_issues(prompt, quality_score)
                            continue
                    
                    # Save the generated content
                    chapter = self.db.query(Chapter).filter(
                        Chapter.story_id == story_id,
                        Chapter.number == chapter_number
                    ).first()
                    
                    if chapter:
                        # Save previous version as revision
                        if chapter.content:
                            self._save_chapter_revision(chapter)
                        
                        # Update with new content
                        chapter.content = result.text
                        chapter.is_generated = True
                        chapter.update_word_count()
                        self.db.commit()
                    
                    return {
                        "success": True,
                        "chapter_content": result.text,
                        "word_count": len(result.text.split()),
                        "target_word_count": target_word_count,
                        "quality_score": quality_score if quality_check else None,
                        "tokens_used": result.tokens_used,
                        "model_used": result.model_used,
                        "generation_attempt": attempt + 1
                    }
                    
            except AIProviderError as e:
                if attempt == self.max_regeneration_attempts - 1:
                    return {
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "attempts_made": attempt + 1
                    }
                # Wait and retry with exponential backoff
                await asyncio.sleep(2 ** attempt)
        
        return {
            "success": False,
            "error": "Failed to generate acceptable content after multiple attempts",
            "attempts_made": self.max_regeneration_attempts
        }
    
    async def generate_chapter_multi_pass(
        self,
        story_id: int,
        chapter_number: int,
        target_word_count: int = 2500
    ) -> Dict[str, Any]:
        """
        Generate a chapter using multi-pass approach for higher quality.
        
        Pass 1: Structure and plot beats
        Pass 2: Character development and dialogue
        Pass 3: Prose refinement and detail enhancement
        """
        context = self.context_service.get_chapter_context(story_id, chapter_number)
        previous_chapters = self._get_previous_chapters(story_id, chapter_number)
        
        try:
            # Pass 1: Structure Generation
            structure_prompt = self._build_structure_prompt(
                context["current_chapter"], context, previous_chapters
            )
            structure_params = GenerationParams(temperature=0.7, max_tokens=1500)
            structure_result = await self.ai_provider.generate_text(structure_prompt, structure_params)
            
            # Pass 2: Character and Dialogue Enhancement
            character_prompt = self._build_character_enhancement_prompt(
                structure_result.text, context, previous_chapters
            )
            character_params = GenerationParams(temperature=0.8, max_tokens=3000)
            character_result = await self.ai_provider.generate_text(character_prompt, character_params)
            
            # Pass 3: Prose Refinement
            prose_prompt = self._build_prose_refinement_prompt(
                character_result.text, target_word_count, context
            )
            prose_params = GenerationParams(temperature=0.6, max_tokens=target_word_count * 2)
            final_result = await self.ai_provider.generate_text(prose_prompt, prose_params)
            
            # Quality assessment of final result
            quality_score = self._assess_content_quality(
                final_result.text, target_word_count, previous_chapters
            )
            
            # Save the generated content
            chapter = self.db.query(Chapter).filter(
                Chapter.story_id == story_id,
                Chapter.number == chapter_number
            ).first()
            
            if chapter:
                if chapter.content:
                    self._save_chapter_revision(chapter)
                
                chapter.content = final_result.text
                chapter.is_generated = True
                chapter.update_word_count()
                self.db.commit()
            
            return {
                "success": True,
                "chapter_content": final_result.text,
                "word_count": len(final_result.text.split()),
                "target_word_count": target_word_count,
                "quality_score": quality_score,
                "generation_method": "multi_pass",
                "passes_completed": 3,
                "total_tokens_used": (
                    structure_result.tokens_used + 
                    character_result.tokens_used + 
                    final_result.tokens_used
                )
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "generation_method": "multi_pass"
            }
    
    def _build_structure_prompt(
        self, 
        chapter_info: Dict[str, Any], 
        context: Dict[str, Any], 
        previous_chapters: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for structural pass."""
        return f"""CHAPTER STRUCTURE GENERATION - PASS 1

Create a detailed structural outline for this chapter that will serve as the foundation for a {2500}-word chapter.

CHAPTER INFO:
Chapter {chapter_info['number']}: {chapter_info.get('title', 'Untitled')}
Summary: {chapter_info.get('summary', 'No summary provided')}

STRUCTURAL REQUIREMENTS:
- Identify 4-6 distinct scenes or moments
- Each scene should be 400-600 words when fully written
- Include specific character actions and plot developments
- Plan dialogue opportunities and character interactions
- Identify moments for internal reflection or character development
- Ensure each scene advances the plot or reveals character

FORMAT YOUR RESPONSE AS:

**SCENE 1: [Scene Title/Location]** (Target: 400-500 words)
Purpose: [What this scene accomplishes for plot/character]
Characters Present: [Who appears in this scene]
Key Events: [Specific things that happen]
Dialogue Opportunities: [What conversations should occur]
Mood/Atmosphere: [Emotional tone to establish]

**SCENE 2: [Scene Title/Location]** (Target: 400-500 words)
[Continue same format...]

[Continue for all scenes...]

**CHAPTER ARC:**
Opening Emotion/Situation: [How the chapter begins]
Closing Emotion/Situation: [How the chapter ends]
Character Development: [How characters change or are revealed]
Plot Advancement: [What story elements progress]

Create a structure that will naturally expand to 2500+ words when fully written with dialogue, description, and character development."""

    def _build_character_enhancement_prompt(
        self, 
        structure: str, 
        context: Dict[str, Any], 
        previous_chapters: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for character development pass."""
        return f"""CHARACTER DEVELOPMENT ENHANCEMENT - PASS 2

Take the structural outline below and develop it into rich character-driven content with authentic dialogue and detailed character interactions.

STRUCTURAL FOUNDATION:
{structure}

CHARACTER ENHANCEMENT REQUIREMENTS:
- Write authentic dialogue that reveals character personality and relationships
- Include character internal thoughts and motivations
- Show character emotions through actions and body language, not exposition
- Create realistic interactions with subtext and tension
- Develop each character's unique voice and speech patterns
- Include moments of character vulnerability or strength
- Show how characters react to conflict and pressure

DIALOGUE REQUIREMENTS:
- Each character must have distinct speech patterns
- Include realistic interruptions, hesitations, and overlapping speech
- Use subtext - characters don't always say what they mean
- Show relationship dynamics through conversation
- Include natural conflict and disagreement
- Avoid exposition dumps disguised as dialogue

WRITE THE ENHANCED VERSION:
Expand each scene with rich character development, authentic dialogue, and detailed character interactions. Each scene should now be substantially longer with specific conversations, character reactions, and internal moments.

Focus on making characters feel like real people with complex motivations and authentic reactions."""

    def _build_prose_refinement_prompt(
        self, 
        character_content: str, 
        target_word_count: int, 
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for prose refinement pass."""
        return f"""PROSE REFINEMENT AND EXPANSION - PASS 3

Take the character-enhanced content below and refine it into polished, publication-quality prose that reaches {target_word_count} words.

CHARACTER-ENHANCED CONTENT:
{character_content}

PROSE REFINEMENT REQUIREMENTS:
- Enhance descriptions with sensory details and atmosphere
- Vary sentence structure and length for better rhythm
- Add environmental details that enhance mood
- Include specific, concrete details instead of vague descriptions
- Eliminate any AI-sounding phrases or clichéd expressions
- Ensure smooth transitions between scenes and paragraphs
- Add texture through specific details and observations

EXPANSION TECHNIQUES:
- Zoom in on crucial emotional moments with detailed description
- Add sensory details (sight, sound, smell, touch, taste)
- Include environmental storytelling through setting details
- Expand character internal experiences and decision-making
- Add atmospheric details that reinforce the mood
- Include specific objects, locations, and physical details
- Show character reactions through micro-expressions and gestures

QUALITY STANDARDS:
- Every sentence must serve a purpose (plot, character, or atmosphere)
- Maintain consistent tone and style throughout
- Ensure the chapter flows naturally from beginning to end
- Reach target word count through quality expansion, not padding
- Create immersive, vivid scenes that engage all senses

WRITE THE FINAL POLISHED CHAPTER:
Create the complete, refined chapter that demonstrates sophisticated prose, rich character development, and engaging storytelling. Target: {target_word_count} words."""

    def _get_enhanced_generation_params(self, target_word_count: int) -> GenerationParams:
        """Get optimized generation parameters for enhanced output."""
        # Adjust parameters based on target length
        max_tokens = min(target_word_count * 2, 8000)  # Allow for longer generation
        
        params = GenerationParams(
            temperature=0.8,  # Higher creativity
            max_tokens=max_tokens,
            top_p=0.95,  # Slightly more focused than pure sampling
            frequency_penalty=0.3,  # Reduce repetition
            presence_penalty=0.2,  # Encourage topic diversity
        )
        
        return params
    
    def _assess_content_quality(
        self, 
        content: str, 
        target_word_count: int, 
        previous_chapters: List[Dict[str, Any]]
    ) -> float:
        """
        Assess the quality of generated content.
        
        Returns a score from 0.0 to 1.0 where 1.0 is highest quality.
        """
        score = 1.0
        word_count = len(content.split())
        
        # Length assessment (30% of score)
        length_ratio = word_count / target_word_count
        if length_ratio < 0.7:  # Too short
            score -= 0.3 * (0.7 - length_ratio) / 0.7
        elif length_ratio < 0.9:  # Slightly short
            score -= 0.1 * (0.9 - length_ratio) / 0.2
        
        # Check for banned phrases (20% of score)
        banned_phrases = [
            "little did", "unbeknownst", "time seemed to slow", "heart pounded",
            "blood ran cold", "breath caught", "world spun", "chill ran down",
            "wave of", "washed over", "couldn't help but", "deep inside told"
        ]
        
        content_lower = content.lower()
        for phrase in banned_phrases:
            if phrase in content_lower:
                score -= 0.04  # -4% per banned phrase, max -20%
        
        # Repetition check (20% of score)
        sentences = content.split('.')
        sentence_starts = [s.strip()[:10] for s in sentences if s.strip()]
        unique_starts = len(set(sentence_starts))
        if len(sentence_starts) > 0:
            start_diversity = unique_starts / len(sentence_starts)
            if start_diversity < 0.8:
                score -= 0.2 * (0.8 - start_diversity) / 0.8
        
        # Dialogue presence (15% of score)
        dialogue_count = content.count('"')
        if dialogue_count < 4:  # Should have some dialogue
            score -= 0.15 * (4 - dialogue_count) / 4
        
        # Paragraph structure (15% of score)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) < 6:  # Should have multiple paragraphs
            score -= 0.15 * (6 - len(paragraphs)) / 6
        
        return max(0.0, min(1.0, score))
    
    def _adjust_prompt_for_quality_issues(self, original_prompt: str, quality_score: float) -> str:
        """Adjust prompt based on quality assessment issues."""
        adjustments = []
        
        if quality_score < 0.6:
            adjustments.extend([
                "",
                "CRITICAL QUALITY ISSUES DETECTED - MANDATORY FIXES:",
                "- MUST reach the target word count through detailed scenes, not summary",
                "- ABSOLUTELY FORBIDDEN to use any clichéd phrases or AI-typical expressions",
                "- REQUIRED: Include substantial dialogue with character-specific voices",
                "- ESSENTIAL: Create multiple distinct scenes with detailed descriptions",
                "- MANDATORY: Vary sentence structure and paragraph length significantly"
            ])
        
        return original_prompt + "\n".join(adjustments)
    
    def _get_previous_chapters(self, story_id: int, chapter_number: int) -> List[Dict[str, Any]]:
        """Get previous chapters for context and continuity."""
        chapters = self.db.query(Chapter).filter(
            Chapter.story_id == story_id,
            Chapter.number < chapter_number
        ).order_by(Chapter.number).all()
        
        return [
            {
                "number": ch.number,
                "title": ch.title,
                "summary": ch.summary,
                "content": ch.content,
                "word_count": ch.word_count
            }
            for ch in chapters
        ]
    
    def _save_chapter_revision(self, chapter: Chapter):
        """Save current chapter content as a revision before updating."""
        if not chapter.content:
            return
        
        # Get next revision number
        last_revision = self.db.query(ChapterRevision).filter(
            ChapterRevision.chapter_id == chapter.chapter_id
        ).order_by(ChapterRevision.revision_number.desc()).first()
        
        next_revision_number = (last_revision.revision_number + 1) if last_revision else 1
        
        # Create revision
        revision = ChapterRevision(
            chapter_id=chapter.chapter_id,
            revision_number=next_revision_number,
            content=chapter.content,
            summary=chapter.summary,
            notes="Auto-saved before regeneration"
        )
        self.db.add(revision)
        self.db.flush()

    async def _generate_chapter_stream_enhanced(
        self,
        story_id: int,
        chapter_number: int,
        prompt: str,
        params: GenerationParams,
        target_word_count: int
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate chapter content with enhanced streaming."""
        try:
            content_buffer = ""
            word_count = 0
            
            async for chunk in self.ai_provider.generate_text_stream(prompt, params):
                content_buffer += chunk
                word_count = len(content_buffer.split())
                
                yield {
                    "type": "chunk",
                    "content": chunk,
                    "total_content": content_buffer,
                    "word_count": word_count,
                    "target_word_count": target_word_count,
                    "progress": min(100, int((word_count / target_word_count) * 100))
                }
            
            # Final quality assessment
            quality_score = self._assess_content_quality(
                content_buffer, target_word_count, 
                self._get_previous_chapters(story_id, chapter_number)
            )
            
            # Save the final content
            chapter = self.db.query(Chapter).filter(
                Chapter.story_id == story_id,
                Chapter.number == chapter_number
            ).first()
            
            if chapter:
                if chapter.content:
                    self._save_chapter_revision(chapter)
                
                chapter.content = content_buffer
                chapter.is_generated = True
                chapter.update_word_count()
                self.db.commit()
            
            yield {
                "type": "complete",
                "success": True,
                "final_content": content_buffer,
                "word_count": word_count,
                "target_word_count": target_word_count,
                "quality_score": quality_score,
                "chapter_id": chapter.chapter_id if chapter else None
            }
            
        except AIProviderError as e:
            yield {
                "type": "error",
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
