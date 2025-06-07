"""
Generation Service for orchestrating AI-powered content creation.

This service handles the multi-step generation process:
- Outline generation
- Character and world element generation  
- Chapter content generation
- AI-assisted editing
"""
import re
from typing import List, Dict, Any, Optional, AsyncGenerator
from sqlalchemy.orm import Session

from models.story import Story, Act
from models.character import Character
from models.world_element import WorldElement
from models.chapter import Chapter, ChapterRevision
from services.ai_providers import create_ai_provider
from services.ai_providers.base import GenerationParams, AIProviderError
from services.context_service import ContextService
from utils.prompt_templates import PromptTemplates
from core.config import settings


class GenerationService:
    """
    Service for orchestrating AI content generation.
    
    Handles the complete pipeline from story idea to finished chapters,
    with human-in-the-loop checkpoints as needed.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the generation service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.ai_provider = create_ai_provider()
        self.context_service = ContextService(db)
        self.prompt_templates = PromptTemplates()
    
    async def generate_outline(
        self, 
        story_id: int, 
        target_chapters: Optional[int] = None,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a story outline with acts and chapters.
        
        Args:
            story_id: ID of the story to generate outline for
            target_chapters: Number of chapters to generate (uses story default if None)
            custom_prompt: Custom prompt override
            
        Returns:
            dict: Generated outline with acts and chapters
            
        Raises:
            ValueError: If story not found
            AIProviderError: If AI generation fails
        """
        story = self.db.query(Story).filter(Story.story_id == story_id).first()
        if not story:
            raise ValueError(f"Story with ID {story_id} not found")
        
        # Use target chapters from parameter or story settings
        num_chapters = target_chapters or story.target_chapters or 20
        
        # Get story context
        context = self.context_service.get_story_context(story_id)
        
        # Build the prompt
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self.prompt_templates.get_outline_prompt(
                story_title=story.title,
                story_description=story.description,
                genre=story.genre,
                target_chapters=num_chapters,
                context=context
            )
        
        # Generate outline using AI with enhanced parameters for plot development
        params = GenerationParams.for_plot_development()
        params.max_tokens = 4000  # Outlines can be long
        
        try:
            result = await self.ai_provider.generate_text(prompt, params)
            outline_text = result.text
            
            # Parse the outline and create database records
            parsed_outline = self._parse_outline(outline_text, story_id)
            
            # Save to database
            self._save_outline_to_db(story_id, parsed_outline)
            
            return {
                "success": True,
                "outline": parsed_outline,
                "raw_text": outline_text,
                "tokens_used": result.tokens_used,
                "model_used": result.model_used,
            }
            
        except AIProviderError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    async def generate_chapter(
        self,
        story_id: int,
        chapter_number: int,
        custom_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate content for a specific chapter.

        Args:
            story_id: ID of the story
            chapter_number: Chapter number to generate
            custom_prompt: Custom prompt override
            stream: Whether to return a streaming response

        Returns:
            dict: Generation result with chapter content
        """
        # Get chapter context
        context = self.context_service.get_chapter_context(story_id, chapter_number)

        if not context.get("current_chapter"):
            raise ValueError(f"Chapter {chapter_number} not found in story outline")

        # Build the prompt
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self.prompt_templates.get_chapter_prompt(
                chapter_info=context["current_chapter"],
                story_context=context,
                previous_chapters=context.get("previous_chapters", []),
                complexity=settings.novel_complexity
            )

        # Generation parameters optimized for creative writing
        params = GenerationParams.for_creative_writing()
        params.max_tokens = 6000  # Chapters can be long

        try:
            if stream:
                return await self._generate_chapter_stream(story_id, chapter_number, prompt, params)
            else:
                result = await self.ai_provider.generate_text(prompt, params)

                # Save the generated content
                chapter = self.db.query(Chapter).filter(
                    Chapter.story_id == story_id,
                    Chapter.number == chapter_number
                ).first()

                if chapter:
                    # Save previous version as revision if content exists
                    if chapter.content:
                        self._save_chapter_revision(chapter)

                    # Update chapter with new content
                    chapter.content = result.text
                    chapter.is_generated = True
                    chapter.update_word_count()
                    self.db.commit()

                return {
                    "success": True,
                    "chapter_content": result.text,
                    "tokens_used": result.tokens_used,
                    "model_used": result.model_used,
                    "word_count": len(result.text.split()),
                }

        except AIProviderError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    async def _generate_chapter_stream(
        self,
        story_id: int,
        chapter_number: int,
        prompt: str,
        params: GenerationParams
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate chapter content with streaming response."""
        try:
            content_buffer = ""
            async for chunk in self.ai_provider.generate_text_stream(prompt, params):
                content_buffer += chunk
                yield {
                    "type": "chunk",
                    "content": chunk,
                    "total_content": content_buffer,
                }

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
                "word_count": len(content_buffer.split()),
            }

        except AIProviderError as e:
            yield {
                "type": "error",
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    async def generate_chapter_stream(
        self,
        story_id: int,
        chapter_number: int,
        custom_prompt: Optional[str] = None
    ):
        """
        Generate chapter content with streaming response.

        Args:
            story_id: ID of the story
            chapter_number: Chapter number to generate
            custom_prompt: Optional custom prompt

        Yields:
            dict: Streaming chunks of generated content
        """
        try:
            # Get context and build prompt (same as non-streaming)
            context = self.context_service.get_story_context(story_id)

            # Get chapter info
            chapter = self.db.query(Chapter).filter(
                Chapter.story_id == story_id,
                Chapter.number == chapter_number
            ).first()

            if not chapter:
                yield {
                    "type": "error",
                    "success": False,
                    "error": f"Chapter {chapter_number} not found"
                }
                return

            # Build prompt
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = self.prompt_templates.get_chapter_generation_prompt(
                    story_context=context,
                    chapter_number=chapter_number,
                    chapter_title=chapter.title,
                    chapter_summary=chapter.summary
                )

            params = GenerationParams(temperature=0.7, max_tokens=4000)

            # Start streaming generation
            yield {
                "type": "start",
                "chapter_number": chapter_number,
                "chapter_title": chapter.title
            }

            # For now, simulate streaming by generating normally and chunking
            # In a real implementation, you'd use the AI provider's streaming API
            result = await self.ai_provider.generate_text(prompt, params)
            content = result.text

            # Simulate streaming by sending chunks
            chunk_size = 50  # words per chunk
            words = content.split()

            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words)

                yield {
                    "type": "content",
                    "chunk": chunk_text + (" " if i + chunk_size < len(words) else ""),
                    "progress": min(100, int((i + chunk_size) / len(words) * 100))
                }

            # Save to database
            self._save_chapter_revision(chapter)
            chapter.content = content
            chapter.is_generated = True
            chapter.word_count = len(words)
            self.db.commit()

            # Send completion
            yield {
                "type": "complete",
                "success": True,
                "chapter_id": chapter.chapter_id,
                "word_count": chapter.word_count,
                "tokens_used": result.tokens_used
            }

        except Exception as e:
            yield {
                "type": "error",
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    def _parse_outline(self, outline_text: str, story_id: int) -> Dict[str, Any]:
        """
        Parse AI-generated outline text into structured data.

        Args:
            outline_text: Raw outline text from AI
            story_id: ID of the story

        Returns:
            dict: Parsed outline structure
        """
        lines = outline_text.strip().split('\n')

        acts = []
        chapters = []
        current_act = None
        current_act_number = 0
        current_chapter = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove markdown formatting
            clean_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
            clean_line = clean_line.strip()

            # Look for act markers (supports various formats)
            # **ACT I: Title** or ACT I: Title or Act 1: Title
            act_match = re.match(r'(?:ACT\s+)?([IVX]+|[0-9]+)[:.]?\s*(.*)', clean_line, re.IGNORECASE)
            if act_match and ('act' in line.lower() or 'ACT' in line):
                current_act_number += 1
                act_title = act_match.group(2).strip() or f"Act {current_act_number}"
                current_act = {
                    "number": current_act_number,
                    "title": act_title,
                    "summary": "",
                }
                acts.append(current_act)
                current_chapter = None  # Reset chapter context
                continue

            # Look for chapter markers
            # **Chapter 1: Title** or Chapter 1: Title
            chapter_match = re.match(r'(?:Chapter\s+)?([0-9]+)[:.]?\s*(.*)', clean_line, re.IGNORECASE)
            if chapter_match and ('chapter' in line.lower() or 'Chapter' in line):
                chapter_number = int(chapter_match.group(1))
                chapter_title = chapter_match.group(2).strip()

                current_chapter = {
                    "number": chapter_number,
                    "title": chapter_title,
                    "summary": "",
                    "act_number": current_act_number if current_act else None,
                }
                chapters.append(current_chapter)
                continue

            # Skip act description lines (lines that start with *In Act...)
            if line.startswith('*In Act') or line.startswith('*In this act'):
                if current_act:
                    if current_act["summary"]:
                        current_act["summary"] += " " + clean_line
                    else:
                        current_act["summary"] = clean_line
                continue

            # Add content to current chapter summary
            if current_chapter and clean_line and not clean_line.startswith('---'):
                # Skip separator lines and empty content
                if current_chapter["summary"]:
                    current_chapter["summary"] += " " + clean_line
                else:
                    current_chapter["summary"] = clean_line
            elif current_act and clean_line and not clean_line.startswith('---'):
                # Add to act summary if no current chapter
                if not current_chapter:
                    if current_act["summary"]:
                        current_act["summary"] += " " + clean_line
                    else:
                        current_act["summary"] = clean_line

        return {
            "acts": acts,
            "chapters": chapters,
        }

    def _save_outline_to_db(self, story_id: int, outline: Dict[str, Any]):
        """
        Save parsed outline to database.

        Args:
            story_id: ID of the story
            outline: Parsed outline structure
        """
        # Clear existing outline
        self.db.query(Chapter).filter(Chapter.story_id == story_id).delete()
        self.db.query(Act).filter(Act.story_id == story_id).delete()

        # Create acts
        act_map = {}
        for act_data in outline.get("acts", []):
            act = Act(
                story_id=story_id,
                number=act_data["number"],
                title=act_data["title"],
                summary=act_data["summary"]
            )
            self.db.add(act)
            self.db.flush()  # Get the ID
            act_map[act_data["number"]] = act.act_id

        # Create chapters
        for chapter_data in outline.get("chapters", []):
            act_id = None
            if chapter_data.get("act_number") and chapter_data["act_number"] in act_map:
                act_id = act_map[chapter_data["act_number"]]

            chapter = Chapter(
                story_id=story_id,
                act_id=act_id,
                number=chapter_data["number"],
                title=chapter_data["title"],
                summary=chapter_data["summary"]
            )
            self.db.add(chapter)

        self.db.commit()

    def _save_chapter_revision(self, chapter: Chapter):
        """
        Save current chapter content as a revision before updating.

        Args:
            chapter: Chapter to save revision for
        """
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

    async def generate_characters(
        self,
        story_id: int,
        character_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate characters for a story based on outline and genre.

        Args:
            story_id: ID of the story
            character_count: Number of characters to generate

        Returns:
            dict: Generated characters
        """
        context = self.context_service.get_story_context(story_id)

        prompt = self.prompt_templates.get_character_generation_prompt(
            story_context=context,
            character_count=character_count or 5,
            complexity=settings.novel_complexity
        )

        # Use enhanced parameters for character creation
        params = GenerationParams.for_character_creation()
        params.max_tokens = 3000

        try:
            result = await self.ai_provider.generate_text(prompt, params)
            characters = self._parse_characters(result.text, story_id)

            # Save to database
            for char_data in characters:
                character = Character(
                    story_id=story_id,
                    name=char_data["name"],
                    role=char_data.get("role"),
                    profile=char_data.get("profile"),
                    personality=char_data.get("personality"),
                    traits=char_data.get("traits"),
                    arc=char_data.get("arc")
                )
                self.db.add(character)

            self.db.commit()

            return {
                "success": True,
                "characters": characters,
                "tokens_used": result.tokens_used,
            }

        except AIProviderError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def _parse_characters(self, characters_text: str, story_id: int) -> List[Dict[str, Any]]:
        """Parse AI-generated character descriptions."""
        # Simplified character parsing - could be enhanced
        characters = []
        current_character = None

        lines = characters_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for character names (usually start with number or bullet)
            name_match = re.match(r'(?:[0-9]+\.|\*|\-)\s*([^:]+)(?::|$)', line)
            if name_match:
                if current_character:
                    characters.append(current_character)

                current_character = {
                    "name": name_match.group(1).strip(),
                    "role": "",
                    "profile": "",
                    "personality": "",
                    "traits": {},
                    "arc": ""
                }
                continue

            # Add details to current character
            if current_character and line:
                if "role:" in line.lower():
                    current_character["role"] = line.split(":", 1)[1].strip()
                elif "age:" in line.lower():
                    current_character["traits"]["age"] = line.split(":", 1)[1].strip()
                elif "appearance:" in line.lower():
                    current_character["traits"]["appearance"] = line.split(":", 1)[1].strip()
                elif "personality:" in line.lower():
                    current_character["personality"] = line.split(":", 1)[1].strip()
                elif "background:" in line.lower():
                    current_character["traits"]["background"] = line.split(":", 1)[1].strip()
                elif "motivation:" in line.lower():
                    current_character["traits"]["motivation"] = line.split(":", 1)[1].strip()
                elif "conflict:" in line.lower():
                    current_character["traits"]["conflict"] = line.split(":", 1)[1].strip()
                elif "skills" in line.lower() or "talents:" in line.lower():
                    current_character["traits"]["skills"] = line.split(":", 1)[1].strip()
                elif "relationships:" in line.lower():
                    current_character["traits"]["relationships"] = line.split(":", 1)[1].strip()
                elif "unique element:" in line.lower():
                    current_character["traits"]["unique_element"] = line.split(":", 1)[1].strip()
                elif "character arc:" in line.lower() or "arc:" in line.lower():
                    current_character["arc"] = line.split(":", 1)[1].strip()
                else:
                    # Add to profile
                    if current_character["profile"]:
                        current_character["profile"] += " " + line
                    else:
                        current_character["profile"] = line

        # Add the last character
        if current_character:
            characters.append(current_character)

        return characters

    async def generate_world_elements(
        self,
        story_id: int,
        element_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate world building elements for a story.

        Args:
            story_id: ID of the story
            element_count: Number of world elements to generate

        Returns:
            dict: Generated world elements
        """
        context = self.context_service.get_story_context(story_id)

        prompt = self.prompt_templates.get_world_building_prompt(
            story_context=context,
            element_count=element_count or 8,
            complexity=settings.novel_complexity
        )

        # Use enhanced parameters for world building
        params = GenerationParams.for_creative_writing()
        params.max_tokens = 4000

        try:
            result = await self.ai_provider.generate_text(prompt, params)
            world_elements = self._parse_world_elements(result.text, story_id)

            # Save to database
            for element_data in world_elements:
                from models.world_element import WorldElement
                world_element = WorldElement(
                    story_id=story_id,
                    name=element_data["name"],
                    element_type=element_data.get("type", "Location"),
                    description=element_data.get("description", ""),
                    significance=element_data.get("significance", ""),
                    details=element_data.get("details", {})
                )
                self.db.add(world_element)

            self.db.commit()

            return {
                "success": True,
                "world_elements": world_elements,
                "tokens_used": result.tokens_used,
            }

        except AIProviderError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def _parse_world_elements(self, world_text: str, story_id: int) -> List[Dict[str, Any]]:
        """Parse AI-generated world building elements."""
        world_elements = []
        current_element = None

        lines = world_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for element names (usually start with number or bullet)
            name_match = re.match(r'(?:[0-9]+\.|\*|\-)\s*([^:]+)(?::|$)', line)
            if name_match:
                if current_element:
                    world_elements.append(current_element)

                current_element = {
                    "name": name_match.group(1).strip(),
                    "type": "Location",
                    "description": "",
                    "significance": "",
                    "details": {},
                    "story_impact": ""
                }
                continue

            # Add details to current element
            if current_element and line:
                if "type:" in line.lower():
                    current_element["type"] = line.split(":", 1)[1].strip()
                elif "description:" in line.lower():
                    current_element["description"] = line.split(":", 1)[1].strip()
                elif "significance:" in line.lower():
                    current_element["significance"] = line.split(":", 1)[1].strip()
                elif "details:" in line.lower():
                    current_element["details"] = {"info": line.split(":", 1)[1].strip()}
                elif "story impact:" in line.lower():
                    current_element["story_impact"] = line.split(":", 1)[1].strip()
                else:
                    # Add to description if no specific field
                    if current_element["description"]:
                        current_element["description"] += " " + line
                    else:
                        current_element["description"] = line

        # Add the last element
        if current_element:
            world_elements.append(current_element)

        return world_elements
