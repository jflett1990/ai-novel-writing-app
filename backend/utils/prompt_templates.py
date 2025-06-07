"""
Prompt templates for AI generation.

This module contains all the prompt templates used for different types
of content generation (outlines, chapters, characters, etc.).
"""
from typing import Dict, Any, List, Optional


class PromptTemplates:
    """
    Collection of prompt templates for AI generation.
    
    These templates can be customized and improved over time to get
    better results from the AI models.
    """
    
    def get_outline_prompt(
        self,
        story_title: str,
        story_description: Optional[str],
        genre: Optional[str],
        target_chapters: int,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate prompt for story outline creation.
        
        Args:
            story_title: Title of the story
            story_description: Story premise/description
            genre: Story genre
            target_chapters: Number of chapters to generate
            context: Additional story context
            
        Returns:
            str: Formatted prompt for outline generation
        """
        prompt_parts = [
            "Generate a highly detailed, innovative novel outline with a multi-layered narrative. Integrate compelling subplots and intricate character arcs that intersect unexpectedly. Deliberately avoid any common literary clichés or predictable story arcs. The outline should hint at hidden motivations, unresolved mysteries, and moral ambiguity, ensuring every narrative element contributes meaningfully and subtly to overarching themes.",
            "",
            f"STORY TITLE: {story_title}",
        ]
        
        if story_description:
            prompt_parts.extend([
                f"STORY PREMISE: {story_description}",
                ""
            ])
        
        if genre:
            prompt_parts.extend([
                f"GENRE: {genre}",
                ""
            ])
        
        prompt_parts.extend([
            f"TARGET LENGTH: {target_chapters} chapters",
            "",
            "Create a compelling story with:",
            "- Character-driven plot that emerges from their choices and flaws",
            "- Genuine conflicts rooted in human complexity",
            "- Surprising but logical story developments",
            "- Avoid overused tropes and predictable beats",
            "",
            "FORMAT YOUR RESPONSE EXACTLY AS:",
            "",
            "ACT I: [Act Title]",
            "[Brief act summary]",
            "",
            "Chapter 1: [Chapter Title]",
            "[Chapter summary - 2-3 sentences describing what happens, who is involved, and what conflict occurs]",
            "",
            "Chapter 2: [Chapter Title]",
            "[Chapter summary - 2-3 sentences describing what happens, who is involved, and what conflict occurs]",
            "",
            "[Continue for all chapters...]",
            "",
            "ACT II: [Act Title]",
            "[Brief act summary]",
            "",
            "[Continue with Act II chapters...]",
            "",
            "ACT III: [Act Title]",
            "[Brief act summary]",
            "",
            "[Continue with Act III chapters...]",
            "",
            "IMPORTANT: Every chapter MUST have a detailed summary. Do not leave any chapter summaries blank.",
            "Focus on original storytelling that avoids clichés while creating a satisfying narrative arc."
        ])
        
        return "\n".join(prompt_parts)
    
    def get_chapter_prompt(
        self,
        chapter_info: Dict[str, Any],
        story_context: Dict[str, Any],
        previous_chapters: List[Dict[str, Any]],
        complexity: str = "standard"
    ) -> str:
        """
        Generate prompt for chapter content creation.

        Args:
            chapter_info: Information about the current chapter
            story_context: Full story context
            previous_chapters: List of previous chapters for continuity

        Returns:
            str: Formatted prompt for chapter generation
        """
        # Get complexity-specific instructions
        complexity_instructions = self._get_complexity_instructions(complexity)

        prompt_parts = [
            "Write a chapter employing varied sentence structures, evocative imagery, and emotionally resonant storytelling. Use narrative restraint to imply rather than explicitly state character intentions and emotional states. Subtly weave thematic threads and foreshadowing without overt exposition. Dialogue should feel organic and reflective of complex interpersonal dynamics. Avoid redundancy, sentimentality, predictable conflicts, or any phrasing that could read as overtly artificial or simplistic.",
            "",
            f"COMPLEXITY LEVEL: {complexity.upper()}",
            *complexity_instructions,
            "",
            "CRITICAL WRITING RULES:",
            "- Use proper punctuation and complete sentences with periods",
            "- Write clear, readable prose - no experimental stream-of-consciousness",
            "- Keep sentences under 25 words and vary their length",
            "- NEVER repeat the same word more than twice in a paragraph",
            "- Write dialogue that sounds like real people talking",
            "- Use concrete, specific details instead of vague abstractions",
            "- Show character emotions through actions and dialogue",
            "- Every sentence must advance the story or reveal character",
            "",
            "ABSOLUTELY FORBIDDEN:",
            "- Writing endless sentences without periods or commas",
            "- Repeating the same word dozens of times in a row",
            "- Lists of synonyms like 'brave valiant heroic gallant stalwart'",
            "- Stream-of-consciousness rambling with no story purpose",
            "- Abstract philosophical rambling that doesn't advance the plot",
            "- Any sentence longer than 50 words",
            "",
            "STORY CONTEXT:",
        ]
        
        # Add story information
        if "story" in story_context:
            story = story_context["story"]
            prompt_parts.extend([
                f"Title: {story.get('title', 'Untitled')}",
                f"Genre: {story.get('genre', 'Fiction')}",
            ])
            if story.get("description"):
                prompt_parts.append(f"Premise: {story['description']}")
        
        # Add character information
        if story_context.get("characters"):
            prompt_parts.extend([
                "",
                "MAIN CHARACTERS:",
            ])
            for char in story_context["characters"][:5]:  # Limit to top 5 characters
                char_line = f"- {char['name']}"
                if char.get("role"):
                    char_line += f" ({char['role']})"
                if char.get("personality"):
                    char_line += f": {char['personality']}"
                prompt_parts.append(char_line)
        
        # Add world elements if any
        if story_context.get("world_elements"):
            prompt_parts.extend([
                "",
                "WORLD/SETTING DETAILS:",
            ])
            for element_type, elements in story_context["world_elements"].items():
                if elements:
                    prompt_parts.append(f"{element_type.title()}:")
                    for element in elements[:3]:  # Limit to top 3 per type
                        prompt_parts.append(f"- {element['name']}: {element.get('description', '')[:100]}...")
        
        # Add previous chapter context
        if previous_chapters:
            prompt_parts.extend([
                "",
                "PREVIOUS CHAPTERS (for continuity):",
            ])
            for prev_ch in previous_chapters[-3:]:  # Last 3 chapters
                prompt_parts.append(f"Chapter {prev_ch['number']}: {prev_ch.get('title', 'Untitled')}")
                if prev_ch.get("summary"):
                    prompt_parts.append(f"  Summary: {prev_ch['summary']}")
        
        # Current chapter instructions
        prompt_parts.extend([
            "",
            "CURRENT CHAPTER TO WRITE:",
            f"Chapter {chapter_info['number']}: {chapter_info.get('title', 'Untitled')}",
        ])
        
        if chapter_info.get("summary"):
            prompt_parts.extend([
                f"Chapter Outline: {chapter_info['summary']}",
                ""
            ])
        
        prompt_parts.extend([
            "",
            "WRITING REQUIREMENTS:",
            "- Length: 1500-2500 words",
            "- Use proper grammar, punctuation, and paragraph breaks",
            "- Write in clear, readable prose - not experimental stream-of-consciousness",
            "- Include dialogue, action, and description in balanced proportions",
            "- End with a compelling hook or transition",
            "- Every sentence should advance the story or reveal character",
            "",
            "Write the complete chapter now. Focus on clarity and readability.",
            "",
            "FINAL REMINDER: Use periods to end sentences. Do not repeat words. Tell a clear story."
        ])"

        
        return "\n".join(prompt_parts)
    
    def get_character_generation_prompt(
        self,
        story_context: Dict[str, Any],
        character_count: int = 5,
        complexity: str = "standard"
    ) -> str:
        """
        Generate prompt for character creation.
        
        Args:
            story_context: Story context for character generation
            character_count: Number of characters to generate
            
        Returns:
            str: Formatted prompt for character generation
        """
        # Get complexity-specific character instructions
        character_complexity = self._get_character_complexity_instructions(complexity)

        prompt_parts = [
            f"Create richly detailed character profiles grounded in realistic psychology. Characters must have complex inner conflicts, believable contradictions, and distinctive mannerisms that subtly reflect their past experiences. Avoid archetypal or stereotypical traits. Include a precise balance of strengths, vulnerabilities, secrets, and unresolved emotional tensions, presenting characters who genuinely evolve in response to layered narrative challenges.",
            "",
            f"COMPLEXITY LEVEL: {complexity.upper()}",
            *character_complexity,
            "",
            "Character Requirements:",
            "- Complex inner conflicts and believable contradictions",
            "- Distinctive mannerisms reflecting past experiences",
            "- Balance of strengths, vulnerabilities, and secrets",
            "- Unresolved emotional tensions",
            "- Genuine evolution potential through narrative challenges",
            "",
            "STORY CONTEXT:",
        ]
        
        if "story" in story_context:
            story = story_context["story"]
            prompt_parts.extend([
                f"Title: {story.get('title', 'Untitled')}",
                f"Genre: {story.get('genre', 'Fiction')}",
            ])
            if story.get("description"):
                prompt_parts.append(f"Premise: {story['description']}")
        
        prompt_parts.extend([
            "",
            "FORMAT YOUR RESPONSE EXACTLY AS:",
            "",
            "1. [Character Name]",
            "Role: [protagonist/antagonist/supporting character]",
            "Age: [Age and life stage]",
            "Appearance: [Physical description - 2-3 specific details]",
            "Personality: [3-4 key traits including contradictions]",
            "Background: [Personal history and formative experiences]",
            "Motivation: [What drives them and what they want]",
            "Conflict: [Internal struggle or flaw]",
            "Skills/Talents: [What they're good at]",
            "Relationships: [How they relate to others]",
            "Unique Element: [Something unexpected or distinctive]",
            "Character Arc: [How they might change through the story]",
            "",
            "2. [Character Name]",
            "[Continue exact same format...]",
            "",
            f"Create exactly {character_count} fully developed characters with complete profiles."
        ])
        
        return "\n".join(prompt_parts)
    
    def get_editing_prompt(
        self,
        original_text: str,
        instruction: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate prompt for AI-assisted editing.
        
        Args:
            original_text: Text to be edited
            instruction: Editing instruction (e.g., "make more suspenseful")
            context: Optional context about the story/chapter
            
        Returns:
            str: Formatted prompt for text editing
        """
        prompt_parts = [
            "Refine the provided text for stylistic sophistication, emotional depth, and narrative complexity. Prioritize subtlety in character portrayals, thematic nuances, and immersive descriptions. Improve sentence rhythm and pacing to avoid monotonous structure. Eliminate predictable phrasing, clichés, superficial profundity, and overtly dramatized expressions. Ensure the final output feels effortlessly human, nuanced, and compelling.",
            "",
            f"EDITING INSTRUCTION: {instruction}",
            ""
        ]
        
        if context:
            prompt_parts.extend([
                f"CONTEXT: {context}",
                ""
            ])
        
        prompt_parts.extend([
            "ORIGINAL TEXT:",
            "---",
            original_text,
            "---",
            "",
            "Please rewrite the text according to the instruction while maintaining the core meaning and narrative flow. Return only the revised text."
        ])
        
        return "\n".join(prompt_parts)

    def _get_complexity_instructions(self, complexity: str) -> List[str]:
        """Get writing instructions based on complexity level."""
        complexity_map = {
            "simple": [
                "- Focus on clear, straightforward storytelling",
                "- Use accessible language and shorter sentences",
                "- Emphasize plot progression and character actions",
                "- Keep descriptions concise but vivid"
            ],
            "standard": [
                "- Balance plot, character development, and description",
                "- Use varied sentence structure and moderate vocabulary",
                "- Include some subtext and deeper character moments",
                "- Develop themes naturally through the story"
            ],
            "complex": [
                "- Weave multiple plot threads and character arcs",
                "- Use sophisticated vocabulary and varied prose styles",
                "- Layer in symbolism, metaphors, and deeper themes",
                "- Include complex character psychology and motivations",
                "- Employ advanced literary techniques (foreshadowing, irony, etc.)"
            ],
            "literary": [
                "- Prioritize prose quality while maintaining readability",
                "- Use sophisticated but clear language and structure",
                "- Explore profound themes through character and plot",
                "- Create layered meaning without sacrificing clarity",
                "- Focus on character psychology and emotional depth",
                "- Employ literary devices purposefully, not for show"
            ]
        }

        return complexity_map.get(complexity, complexity_map["standard"])

    def _get_character_complexity_instructions(self, complexity: str) -> List[str]:
        """Get character creation instructions based on complexity level."""
        complexity_map = {
            "simple": [
                "- Create clear, easily understood character roles and motivations",
                "- Focus on one main trait or goal per character",
                "- Keep character backgrounds straightforward"
            ],
            "standard": [
                "- Develop characters with 2-3 key personality traits",
                "- Give each character a clear motivation and one meaningful flaw",
                "- Include some character growth potential"
            ],
            "complex": [
                "- Create multi-faceted characters with internal contradictions",
                "- Develop complex psychological profiles and hidden depths",
                "- Include intricate relationships and power dynamics",
                "- Give characters multiple, sometimes conflicting motivations"
            ],
            "literary": [
                "- Craft characters as vehicles for exploring deep themes",
                "- Create complex psychological portraits with rich interiority",
                "- Develop characters that embody philosophical concepts",
                "- Include subtle character symbolism and archetypal elements"
            ]
        }

        return complexity_map.get(complexity, complexity_map["standard"])

    def get_world_building_prompt(
        self,
        story_context: Dict[str, Any],
        element_count: int = 8,
        complexity: str = "standard"
    ) -> str:
        """
        Generate prompt for world building elements.

        Args:
            story_context: Story context for world building
            element_count: Number of world elements to generate
            complexity: Complexity level

        Returns:
            str: Formatted prompt for world building
        """
        # Get complexity-specific world building instructions
        world_complexity = self._get_world_complexity_instructions(complexity)

        prompt_parts = [
            f"Design an original, vividly immersive world grounded in subtle logic and internal consistency. Provide intriguing cultural practices, unique societal structures, and nuanced historical undercurrents. Every element should seamlessly enrich the narrative and subtly inform character behaviors and plot developments. Avoid typical fantasy, dystopian, or science-fiction tropes. Prioritize complexity, detail, and originality.",
            "",
            f"COMPLEXITY LEVEL: {complexity.upper()}",
            *world_complexity,
            "",
            "STORY CONTEXT:",
        ]

        if "story" in story_context:
            story = story_context["story"]
            prompt_parts.extend([
                f"Title: {story.get('title', 'Untitled')}",
                f"Genre: {story.get('genre', 'Fiction')}",
            ])
            if story.get("description"):
                prompt_parts.append(f"Premise: {story['description']}")

        prompt_parts.extend([
            "",
            "Create diverse world elements:",
            "- Locations (cities, buildings, landscapes)",
            "- Organizations (governments, guilds, companies)",
            "- Cultures and societies",
            "- Technologies or magic systems",
            "- Historical events",
            "- Customs and traditions",
            "",
            "FORMAT YOUR RESPONSE EXACTLY AS:",
            "",
            "1. [Element Name]",
            "Type: [Location/Organization/Culture/Technology/History/Custom]",
            "Description: [Detailed description of what this is]",
            "Significance: [Why this matters to the story]",
            "Details: [Specific features, rules, or characteristics]",
            "Story Impact: [How this affects characters or plot]",
            "",
            "2. [Element Name]",
            "[Continue exact same format...]",
            "",
            f"Create exactly {element_count} world building elements that enrich the story."
        ])

        return "\n".join(prompt_parts)

    def _get_world_complexity_instructions(self, complexity: str) -> List[str]:
        """Get world building instructions based on complexity level."""
        complexity_map = {
            "simple": [
                "- Create clear, easily understood world elements",
                "- Focus on elements that directly impact the story",
                "- Keep world rules straightforward"
            ],
            "standard": [
                "- Develop a believable, consistent world",
                "- Include both major and minor world elements",
                "- Create some depth beyond the immediate story"
            ],
            "complex": [
                "- Build a rich, multi-layered world with intricate systems",
                "- Include complex political, social, or magical systems",
                "- Create interconnected world elements with deep history"
            ],
            "literary": [
                "- Craft world elements that serve thematic purposes",
                "- Use setting as a reflection of character psychology",
                "- Create symbolic or metaphorical world elements"
            ]
        }

        return complexity_map.get(complexity, complexity_map["standard"])

    def get_dialogue_prompt(
        self,
        characters: List[str],
        scene_context: str,
        emotional_subtext: str = ""
    ) -> str:
        """
        Generate prompt for authentic dialogue crafting.

        Args:
            characters: List of character names in the scene
            scene_context: Context of the scene
            emotional_subtext: Hidden emotional dynamics

        Returns:
            str: Formatted prompt for dialogue generation
        """
        prompt_parts = [
            "Compose authentic, character-specific dialogue that reflects realistic conversational rhythms, emotional subtext, and interpersonal tension. Dialogue must subtly reveal hidden motivations, unspoken anxieties, and nuanced shifts in relationship dynamics. Avoid direct exposition, unnatural eloquence, obvious emotional statements, or repetitive speech patterns. Aim for dialogues that feel spontaneous, layered, and psychologically realistic.",
            "",
            f"SCENE CONTEXT: {scene_context}",
            f"CHARACTERS: {', '.join(characters)}",
        ]

        if emotional_subtext:
            prompt_parts.append(f"EMOTIONAL SUBTEXT: {emotional_subtext}")

        prompt_parts.extend([
            "",
            "DIALOGUE REQUIREMENTS:",
            "- Each character must have a distinct voice and speech pattern",
            "- Include realistic interruptions, pauses, and natural flow",
            "- Layer in subtext - what they don't say is as important as what they do",
            "- Show power dynamics and relationship tensions through word choice",
            "- Avoid exposition dumps or characters explaining things they already know",
            "- Use realistic contractions and speech patterns",
            "",
            "Write the dialogue scene now:"
        ])

        return "\n".join(prompt_parts)

    def get_plot_twist_prompt(
        self,
        story_context: Dict[str, Any],
        existing_events: List[str],
        twist_type: str = "revelation"
    ) -> str:
        """
        Generate prompt for sophisticated plot twists.

        Args:
            story_context: Current story context
            existing_events: List of events that have already occurred
            twist_type: Type of twist (revelation, betrayal, identity, etc.)

        Returns:
            str: Formatted prompt for plot twist generation
        """
        prompt_parts = [
            "Design a genuinely surprising, yet believable plot twist or revelation that recontextualizes previous narrative events without relying on improbable coincidences or deus ex machina. The twist should deepen thematic resonance, significantly alter character dynamics, and invite layered reinterpretations of earlier scenes. Avoid predictable tropes or contrived shock value; prioritize narrative logic and emotional authenticity.",
            "",
            f"TWIST TYPE: {twist_type}",
            "",
            "STORY CONTEXT:",
        ]

        if "story" in story_context:
            story = story_context["story"]
            prompt_parts.extend([
                f"Title: {story.get('title', 'Untitled')}",
                f"Genre: {story.get('genre', 'Fiction')}",
            ])
            if story.get("description"):
                prompt_parts.append(f"Premise: {story['description']}")

        if existing_events:
            prompt_parts.extend([
                "",
                "EXISTING EVENTS:",
                *[f"- {event}" for event in existing_events],
            ])

        prompt_parts.extend([
            "",
            "TWIST REQUIREMENTS:",
            "- Must be surprising but feel inevitable in hindsight",
            "- Should recontextualize at least 2-3 previous events",
            "- Must be grounded in established character motivations",
            "- Should deepen rather than simplify the story's themes",
            "- Avoid coincidences, hidden twins, or 'it was all a dream'",
            "",
            "Describe the plot twist and how it reframes the story:"
        ])

        return "\n".join(prompt_parts)
