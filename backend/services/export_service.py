"""
Export service for generating PDF and Markdown exports of stories.
"""
import os
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from models.story import Story
from models.chapter import Chapter
from db.database import get_db


class ExportService:
    """Service for exporting stories to various formats."""
    
    def __init__(self):
        self.export_dir = "exports"
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_story_markdown(self, story_id: int, db: Session) -> str:
        """
        Export a story to Markdown format.
        
        Args:
            story_id: ID of the story to export
            db: Database session
            
        Returns:
            Path to the exported Markdown file
        """
        story = db.query(Story).filter(Story.story_id == story_id).first()
        if not story:
            raise ValueError(f"Story with ID {story_id} not found")
        
        # Get all chapters ordered by number
        chapters = db.query(Chapter).filter(
            Chapter.story_id == story_id,
            Chapter.is_generated == True
        ).order_by(Chapter.number).all()
        
        # Generate Markdown content
        markdown_content = self._generate_markdown_content(story, chapters)
        
        # Save to file
        filename = f"{story.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath
    
    def export_story_text(self, story_id: int, db: Session) -> str:
        """
        Export a story to plain text format.
        
        Args:
            story_id: ID of the story to export
            db: Database session
            
        Returns:
            Path to the exported text file
        """
        story = db.query(Story).filter(Story.story_id == story_id).first()
        if not story:
            raise ValueError(f"Story with ID {story_id} not found")
        
        # Get all chapters ordered by number
        chapters = db.query(Chapter).filter(
            Chapter.story_id == story_id,
            Chapter.is_generated == True
        ).order_by(Chapter.number).all()
        
        # Generate text content
        text_content = self._generate_text_content(story, chapters)
        
        # Save to file
        filename = f"{story.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        return filepath
    
    def _generate_markdown_content(self, story: Story, chapters: list[Chapter]) -> str:
        """Generate Markdown content for the story."""
        content = []
        
        # Title and metadata
        content.append(f"# {story.title}")
        content.append("")
        
        if story.description:
            content.append(f"*{story.description}*")
            content.append("")
        
        # Metadata table
        content.append("## Story Information")
        content.append("")
        content.append("| Field | Value |")
        content.append("|-------|-------|")
        content.append(f"| Genre | {story.genre or 'Not specified'} |")
        content.append(f"| Target Chapters | {story.target_chapters} |")
        content.append(f"| Target Word Count | {story.target_word_count:,} |")
        content.append(f"| Generated Chapters | {len(chapters)} |")
        
        # Calculate total word count
        total_words = sum(chapter.word_count or 0 for chapter in chapters)
        content.append(f"| Current Word Count | {total_words:,} |")
        content.append(f"| Created | {story.created_at.strftime('%Y-%m-%d %H:%M:%S')} |")
        content.append("")
        
        # Table of contents
        content.append("## Table of Contents")
        content.append("")
        for chapter in chapters:
            content.append(f"- [Chapter {chapter.number}: {chapter.title}](#chapter-{chapter.number}-{chapter.title.lower().replace(' ', '-')})")
        content.append("")
        
        # Chapters
        for chapter in chapters:
            content.append(f"## Chapter {chapter.number}: {chapter.title}")
            content.append("")
            
            if chapter.summary:
                content.append(f"*{chapter.summary}*")
                content.append("")
            
            if chapter.content:
                # Clean up the content (remove markdown formatting if present)
                chapter_content = chapter.content.strip()
                if chapter_content.startswith(f"**Chapter {chapter.number}:"):
                    # Remove the title if it's already in the content
                    lines = chapter_content.split('\n')
                    if lines[0].startswith("**Chapter"):
                        chapter_content = '\n'.join(lines[1:]).strip()
                
                content.append(chapter_content)
            else:
                content.append("*Chapter content not yet generated.*")
            
            content.append("")
            content.append("---")
            content.append("")
        
        # Footer
        content.append(f"*Generated by AI Novel Writer on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return '\n'.join(content)
    
    def _generate_text_content(self, story: Story, chapters: list[Chapter]) -> str:
        """Generate plain text content for the story."""
        content = []
        
        # Title and metadata
        content.append(story.title.upper())
        content.append("=" * len(story.title))
        content.append("")
        
        if story.description:
            content.append(story.description)
            content.append("")
        
        # Metadata
        content.append("STORY INFORMATION")
        content.append("-" * 17)
        content.append(f"Genre: {story.genre or 'Not specified'}")
        content.append(f"Target Chapters: {story.target_chapters}")
        content.append(f"Target Word Count: {story.target_word_count:,}")
        content.append(f"Generated Chapters: {len(chapters)}")
        
        # Calculate total word count
        total_words = sum(chapter.word_count or 0 for chapter in chapters)
        content.append(f"Current Word Count: {total_words:,}")
        content.append(f"Created: {story.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # Chapters
        for i, chapter in enumerate(chapters):
            if i > 0:
                content.append("\n" + "=" * 80 + "\n")
            
            content.append(f"CHAPTER {chapter.number}: {chapter.title.upper()}")
            content.append("-" * (len(f"CHAPTER {chapter.number}: {chapter.title}") + 5))
            content.append("")
            
            if chapter.summary:
                content.append(f"Summary: {chapter.summary}")
                content.append("")
            
            if chapter.content:
                # Clean up the content
                chapter_content = chapter.content.strip()
                if chapter_content.startswith(f"**Chapter {chapter.number}:"):
                    # Remove markdown formatting
                    lines = chapter_content.split('\n')
                    if lines[0].startswith("**Chapter"):
                        chapter_content = '\n'.join(lines[1:]).strip()
                
                # Remove other markdown formatting
                chapter_content = chapter_content.replace("**", "").replace("*", "")
                content.append(chapter_content)
            else:
                content.append("Chapter content not yet generated.")
            
            content.append("")
        
        # Footer
        content.append("\n" + "=" * 80)
        content.append(f"Generated by AI Novel Writer on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return '\n'.join(content)


# Global instance
export_service = ExportService()
