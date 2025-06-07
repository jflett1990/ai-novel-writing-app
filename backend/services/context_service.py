"""
Context Service for assembling AI prompts with story context.

This service retrieves relevant information from the database (characters, 
world elements, previous plot points) and constructs prompts with that context.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from models.story import Story
from models.character import Character
from models.world_element import WorldElement
from models.chapter import Chapter


class ContextService:
    """
    Service for managing context injection into AI prompts.
    
    This service helps maintain consistency by providing the AI with
    relevant story information when generating content.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the context service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_story_context(self, story_id: int) -> Dict[str, Any]:
        """
        Get comprehensive context for a story.
        
        Args:
            story_id: ID of the story
            
        Returns:
            dict: Story context including basic info, characters, and world elements
        """
        story = self.db.query(Story).filter(Story.story_id == story_id).first()
        if not story:
            return {}
        
        context = {
            "story": {
                "title": story.title,
                "description": story.description,
                "genre": story.genre,
                "target_word_count": story.target_word_count,
                "target_chapters": story.target_chapters,
            },
            "characters": self._get_characters_context(story_id),
            "world_elements": self._get_world_elements_context(story_id),
            "outline": self._get_outline_context(story_id),
        }
        
        return context
    
    def get_chapter_context(self, story_id: int, chapter_number: int) -> Dict[str, Any]:
        """
        Get context specific to generating a particular chapter.
        
        Args:
            story_id: ID of the story
            chapter_number: Chapter number to generate
            
        Returns:
            dict: Chapter-specific context
        """
        # Get base story context
        context = self.get_story_context(story_id)
        
        # Get the specific chapter info
        chapter = self.db.query(Chapter).filter(
            Chapter.story_id == story_id,
            Chapter.number == chapter_number
        ).first()
        
        if chapter:
            context["current_chapter"] = {
                "number": chapter.number,
                "title": chapter.title,
                "summary": chapter.summary,
            }
        
        # Get previous chapters for continuity
        previous_chapters = self.db.query(Chapter).filter(
            Chapter.story_id == story_id,
            Chapter.number < chapter_number,
            Chapter.content.isnot(None)  # Only chapters with content
        ).order_by(Chapter.number).all()
        
        context["previous_chapters"] = [
            {
                "number": ch.number,
                "title": ch.title,
                "summary": ch.summary,
                "word_count": ch.word_count,
            }
            for ch in previous_chapters
        ]
        
        # Get upcoming chapters for foreshadowing
        upcoming_chapters = self.db.query(Chapter).filter(
            Chapter.story_id == story_id,
            Chapter.number > chapter_number
        ).order_by(Chapter.number).limit(3).all()  # Next 3 chapters
        
        context["upcoming_chapters"] = [
            {
                "number": ch.number,
                "title": ch.title,
                "summary": ch.summary,
            }
            for ch in upcoming_chapters
        ]
        
        return context
    
    def _get_characters_context(self, story_id: int) -> List[Dict[str, Any]]:
        """Get character context for the story."""
        characters = self.db.query(Character).filter(
            Character.story_id == story_id
        ).all()
        
        return [
            {
                "name": char.name,
                "role": char.role,
                "personality": char.personality,
                "motivations": char.motivations,
                "arc": char.arc,
                "traits": char.traits,
            }
            for char in characters
        ]
    
    def _get_world_elements_context(self, story_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get world elements context grouped by type."""
        world_elements = self.db.query(WorldElement).filter(
            WorldElement.story_id == story_id
        ).all()
        
        # Group by type
        grouped_elements = {}
        for element in world_elements:
            element_type = element.type
            if element_type not in grouped_elements:
                grouped_elements[element_type] = []
            
            grouped_elements[element_type].append({
                "name": element.name,
                "description": element.description,
                "category": element.category,
                "importance": element.importance,
                "meta": element.meta,
            })
        
        return grouped_elements
    
    def _get_outline_context(self, story_id: int) -> List[Dict[str, Any]]:
        """Get outline context (all chapters with summaries)."""
        chapters = self.db.query(Chapter).filter(
            Chapter.story_id == story_id
        ).order_by(Chapter.number).all()
        
        return [
            {
                "number": ch.number,
                "title": ch.title,
                "summary": ch.summary,
                "is_generated": ch.is_generated,
                "word_count": ch.word_count,
            }
            for ch in chapters
        ]
    
    def format_context_for_prompt(self, context: Dict[str, Any], context_type: str = "full") -> str:
        """
        Format context information into a string suitable for AI prompts.
        
        Args:
            context: Context dictionary from get_story_context or get_chapter_context
            context_type: Type of context formatting ("full", "summary", "minimal")
            
        Returns:
            str: Formatted context string
        """
        if context_type == "minimal":
            return self._format_minimal_context(context)
        elif context_type == "summary":
            return self._format_summary_context(context)
        else:
            return self._format_full_context(context)
    
    def _format_full_context(self, context: Dict[str, Any]) -> str:
        """Format full context with all available information."""
        sections = []
        
        # Story information
        if "story" in context:
            story = context["story"]
            sections.append(f"STORY: {story.get('title', 'Untitled')}")
            if story.get("description"):
                sections.append(f"PREMISE: {story['description']}")
            if story.get("genre"):
                sections.append(f"GENRE: {story['genre']}")
        
        # Characters
        if "characters" in context and context["characters"]:
            sections.append("\nCHARACTERS:")
            for char in context["characters"]:
                char_info = f"- {char['name']}"
                if char.get("role"):
                    char_info += f" ({char['role']})"
                if char.get("personality"):
                    char_info += f": {char['personality']}"
                sections.append(char_info)
        
        # World elements
        if "world_elements" in context:
            for element_type, elements in context["world_elements"].items():
                if elements:
                    sections.append(f"\n{element_type.upper().replace('_', ' ')}:")
                    for element in elements:
                        sections.append(f"- {element['name']}: {element.get('description', '')}")
        
        # Current chapter (if applicable)
        if "current_chapter" in context:
            ch = context["current_chapter"]
            sections.append(f"\nCURRENT CHAPTER: Chapter {ch['number']}")
            if ch.get("title"):
                sections.append(f"Title: {ch['title']}")
            if ch.get("summary"):
                sections.append(f"Summary: {ch['summary']}")
        
        return "\n".join(sections)
    
    def _format_summary_context(self, context: Dict[str, Any]) -> str:
        """Format summary context with key information only."""
        sections = []
        
        if "story" in context:
            story = context["story"]
            sections.append(f"Story: {story.get('title', 'Untitled')}")
            if story.get("description"):
                sections.append(f"Premise: {story['description']}")
        
        # Key characters only
        if "characters" in context:
            main_chars = [c for c in context["characters"] if c.get("role") in ["protagonist", "antagonist"]]
            if main_chars:
                char_names = [c["name"] for c in main_chars]
                sections.append(f"Main Characters: {', '.join(char_names)}")
        
        return "\n".join(sections)
    
    def _format_minimal_context(self, context: Dict[str, Any]) -> str:
        """Format minimal context with just essential information."""
        if "story" in context:
            story = context["story"]
            return f"Story: {story.get('title', 'Untitled')}"
        return ""
