"""
Enhanced Prompt Templates for AI Novel Generation.

This module contains significantly improved prompt templates designed to generate
longer, more original, and higher-quality content that avoids AI writing clichés.
"""
from typing import Dict, Any, List, Optional
import random


class EnhancedPromptTemplates:
    """
    Advanced prompt templates with anti-generic measures and length optimization.
    """
    
    def __init__(self):
        self.anti_generic_phrases = self._load_anti_generic_database()
        self.style_variations = self._load_style_variations()
        self.narrative_devices = self._load_narrative_devices()
    
    def get_enhanced_chapter_prompt(
        self,
        chapter_info: Dict[str, Any],
        story_context: Dict[str, Any],
        previous_chapters: List[Dict[str, Any]],
        complexity: str = "standard",
        target_word_count: int = 2500
    ) -> str:
        """
        Generate an enhanced prompt for chapter creation with strict anti-generic measures.
        """
        # Analyze previous content for patterns to avoid
        previous_analysis = self._analyze_previous_chapters(previous_chapters)
        
        # Select narrative devices to emphasize
        selected_devices = self._select_narrative_devices(chapter_info, story_context)
        
        # Build the enhanced prompt
        prompt_parts = [
            self._get_advanced_writing_directive(target_word_count),
            "",
            self._get_anti_generic_constraints(),
            "",
            self._get_length_enforcement_rules(target_word_count),
            "",
            self._get_originality_requirements(),
            "",
            self._get_narrative_sophistication_rules(selected_devices),
            "",
            self._get_context_section(story_context, chapter_info),
            "",
            self._get_previous_chapter_continuity(previous_chapters, previous_analysis),
            "",
            self._get_chapter_specific_requirements(chapter_info, target_word_count),
            "",
            self._get_final_execution_instructions(target_word_count)
        ]
        
        return "\n".join(prompt_parts)
    
    def _get_advanced_writing_directive(self, target_word_count: int) -> str:
        """Core writing directive with specific requirements."""
        return f"""ADVANCED CHAPTER COMPOSITION DIRECTIVE:

Write a substantial chapter of exactly {target_word_count} words that demonstrates sophisticated literary craftsmanship. This chapter must exhibit:

1. NARRATIVE DENSITY: Every paragraph must advance plot, reveal character, or deepen atmosphere
2. LINGUISTIC SOPHISTICATION: Varied sentence structures, precise vocabulary, natural rhythm
3. ORIGINALITY IMPERATIVE: Completely avoid all AI writing patterns and generic expressions
4. IMMERSIVE DETAIL: Rich sensory descriptions that create vivid mental imagery
5. CHARACTER AUTHENTICITY: Dialogue and actions that feel genuinely human
6. PACING MASTERY: Balanced mix of action, dialogue, reflection, and description

CRITICAL: This chapter must feel like it was written by a skilled human novelist, not an AI."""

    def _get_anti_generic_constraints(self) -> str:
        """Comprehensive list of things to absolutely avoid."""
        return """ABSOLUTELY FORBIDDEN - IMMEDIATE DISQUALIFICATION IF USED:

BANNED PHRASES AND PATTERNS:
- "Little did [they/he/she] know" or any variation
- "Unbeknownst to [character]" 
- "The [noun] that would change everything"
- "A chill ran down [their] spine"
- "Time seemed to slow"
- "The air was thick with tension"
- "A sense of [emotion] washed over [them]"
- "Their heart pounded in their chest"
- "A wave of [emotion] crashed over [them]"
- "[Character] couldn't help but think"
- "Something deep inside told [them]"
- "The weight of [situation] pressed down"
- "A flicker of [emotion] crossed their face"

BANNED SENTENCE STRUCTURES:
- Starting more than 2 sentences per paragraph with "The" or "A"
- Using "As [action], [consequence]" more than once per 1000 words
- Sentences longer than 35 words
- More than 2 sentences starting with "He/She/They" per paragraph
- Rhetorical questions unless in dialogue

BANNED WRITING PATTERNS:
- Purple prose or overwrought descriptions
- Constant emotional state announcements ("He felt angry")
- Action sequences that read like stage directions
- Dialogue tags other than said/asked (except sparingly)
- Info-dumping disguised as character thoughts"""

    def _get_length_enforcement_rules(self, target_word_count: int) -> str:
        """Rules to ensure adequate chapter length."""
        min_words = int(target_word_count * 0.9)
        max_words = int(target_word_count * 1.1)
        
        return f"""MANDATORY LENGTH REQUIREMENTS:

TARGET: {target_word_count} words (Range: {min_words}-{max_words} words)

TO ACHIEVE PROPER LENGTH:
- Minimum 8-12 substantial paragraphs
- Each paragraph: 150-300 words
- Include 3-4 distinct scenes or moments within the chapter
- Develop at least 2-3 character interactions or internal moments
- Show, don't tell - expand moments through sensory detail
- Include subtext in dialogue - characters talking around topics
- Use environmental details to enhance mood and atmosphere
- Incorporate backstory naturally through character reflection
- Add meaningful action sequences that serve character development

PACING STRUCTURE:
- Opening: Hook with immediate engagement (200-300 words)
- Development: 2-3 substantial scenes (600-800 words each)
- Character moments: Internal reflection or dialogue (300-400 words)
- Conclusion: Chapter ending with forward momentum (200-300 words)

EXPANSION TECHNIQUES:
- Zoom in on crucial moments with detailed description
- Show character decision-making processes
- Include environmental storytelling
- Develop subplot elements
- Add texture through specific, concrete details"""

    def _get_originality_requirements(self) -> str:
        """Requirements for original, non-generic content."""
        return """ORIGINALITY MANDATES:

UNIQUE VOICE REQUIREMENTS:
- Every character must have distinct speech patterns, vocabulary, and rhythm
- Dialogue should reveal personality without exposition
- Characters should misunderstand each other realistically
- Include natural interruptions, hesitations, and subtext

FRESH DESCRIPTION METHODS:
- Use unexpected but accurate metaphors
- Focus on specific, concrete details rather than vague impressions
- Connect descriptions to character perspective and mood
- Avoid tired comparisons (brave as a lion, quiet as a mouse, etc.)

AUTHENTIC CONFLICT:
- Conflicts arise from character flaws and competing desires
- No convenient coincidences or easy solutions
- Problems create new problems
- Characters make imperfect decisions based on incomplete information

NARRATIVE SURPRISE:
- Include subtle details that gain significance later
- Characters have mixed motives and hidden depths
- Small moments reveal character as much as big dramatic beats
- Use misdirection through character assumptions, not author manipulation"""

    def _get_narrative_sophistication_rules(self, selected_devices: List[str]) -> str:
        """Advanced narrative techniques to employ."""
        devices_text = "\n".join([f"- {device}" for device in selected_devices])
        
        return f"""NARRATIVE SOPHISTICATION REQUIREMENTS:

EMPLOY THESE TECHNIQUES:
{devices_text}

ADVANCED STORYTELLING ELEMENTS:
- Use dramatic irony where readers know more than characters
- Layer multiple meanings in dialogue and action
- Create parallels and contrasts between characters and situations
- Use setting and weather to reinforce emotional states without stating them
- Include symbolic elements that serve the story naturally
- Build tension through what characters DON'T say or do
- Use time and memory strategically to reveal information

CHARACTER DEPTH REQUIREMENTS:
- Characters should surprise themselves with their reactions
- Include moments where characters act against type for reasons
- Show how past experiences influence present decisions
- Reveal character through choices under pressure
- Use body language and micro-expressions to show internal states

DIALOGUE SOPHISTICATION:
- Characters speak in subtext - meaning beneath surface words
- Include realistic interruptions, false starts, and overlapping speech
- Each character has unique vocabulary, sentence structure, and rhythms
- Dialogue should reveal relationship dynamics and power structures
- Use silence and what's not said as powerfully as words"""

    def _get_context_section(self, story_context: Dict[str, Any], chapter_info: Dict[str, Any]) -> str:
        """Build context section from story data."""
        context_parts = ["STORY CONTEXT FOR CONSISTENCY:"]
        
        if "story" in story_context:
            story = story_context["story"]
            context_parts.extend([
                f"Title: {story.get('title', 'Untitled')}",
                f"Genre: {story.get('genre', 'Fiction')}",
            ])
            if story.get("description"):
                context_parts.append(f"Premise: {story['description']}")
        
        # Add character information
        if story_context.get("characters"):
            context_parts.extend([
                "",
                "MAIN CHARACTERS (maintain consistency):"
            ])
            for char in story_context["characters"][:5]:
                char_line = f"- {char['name']}"
                if char.get("role"):
                    char_line += f" ({char['role']})"
                if char.get("personality"):
                    char_line += f": {char['personality'][:100]}..."
                if char.get("speech_pattern"):
                    char_line += f" | Speech: {char['speech_pattern']}"
                context_parts.append(char_line)
        
        # Add world elements
        if story_context.get("world_elements"):
            context_parts.extend([
                "",
                "WORLD/SETTING ELEMENTS:"
            ])
            for element_type, elements in story_context["world_elements"].items():
                if elements:
                    for element in elements[:3]:
                        context_parts.append(f"- {element['name']} ({element_type}): {element.get('description', '')[:100]}...")
        
        return "\n".join(context_parts)

    def _get_previous_chapter_continuity(self, previous_chapters: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
        """Build continuity requirements based on previous chapters."""
        if not previous_chapters:
            return "STORY OPENING: This is the beginning - establish tone, introduce key elements, create immediate engagement."
        
        continuity_parts = [
            "CONTINUITY REQUIREMENTS:",
            "",
            "RECENT EVENTS TO BUILD FROM:"
        ]
        
        # Show last 2-3 chapters for context
        for prev_ch in previous_chapters[-3:]:
            continuity_parts.append(f"Chapter {prev_ch['number']}: {prev_ch.get('title', 'Untitled')}")
            if prev_ch.get("summary"):
                continuity_parts.append(f"  Summary: {prev_ch['summary']}")
        
        # Add style consistency requirements
        continuity_parts.extend([
            "",
            "STYLE CONSISTENCY REQUIREMENTS:",
            f"- Maintain established tone and pacing patterns",
            f"- Continue character voice consistency established in previous chapters",
            f"- Build on emotional threads and relationship developments",
            f"- Reference previous events naturally when relevant",
            f"- Escalate or develop conflicts introduced earlier"
        ])
        
        # Add specific warnings based on analysis
        if analysis.get("repetitive_phrases"):
            continuity_parts.append(f"- AVOID these phrases used in previous chapters: {', '.join(analysis['repetitive_phrases'][:5])}")
        
        if analysis.get("overused_words"):
            continuity_parts.append(f"- MINIMIZE these overused words: {', '.join(analysis['overused_words'][:5])}")
        
        return "\n".join(continuity_parts)

    def _get_chapter_specific_requirements(self, chapter_info: Dict[str, Any], target_word_count: int) -> str:
        """Requirements specific to this chapter."""
        requirements = [
            "CURRENT CHAPTER REQUIREMENTS:",
            "",
            f"Chapter {chapter_info['number']}: {chapter_info.get('title', 'Untitled')}",
        ]
        
        if chapter_info.get("summary"):
            requirements.extend([
                f"Chapter Outline: {chapter_info['summary']}",
                "",
                "EXPANSION INSTRUCTIONS:",
                "- The outline above is a skeleton - flesh it out with rich detail",
                "- Add scenes, dialogue, and character moments not mentioned in the outline",
                "- Develop the emotional journey of each character in this chapter",
                "- Include environmental details that enhance the mood",
                "- Show character relationships evolving through their interactions"
            ])
        
        # Chapter-specific requirements based on position in story
        chapter_num = chapter_info.get('number', 1)
        if chapter_num == 1:
            requirements.extend([
                "",
                "OPENING CHAPTER REQUIREMENTS:",
                "- Establish the protagonist's ordinary world and initial situation",
                "- Introduce the central conflict or inciting incident",
                "- Create immediate engagement without info-dumping",
                "- Establish the story's tone and writing style",
                "- End with a hook that compels readers to continue"
            ])
        elif chapter_num <= 3:
            requirements.extend([
                "",
                "EARLY CHAPTER REQUIREMENTS:",
                "- Deepen character establishment and world-building",
                "- Escalate initial conflicts or introduce complications",
                "- Develop relationships between characters",
                "- Build momentum toward major plot developments",
                "- Maintain the pacing and tone established in Chapter 1"
            ])
        else:
            requirements.extend([
                "",
                "CONTINUING CHAPTER REQUIREMENTS:",
                "- Advance major plot threads significantly",
                "- Develop character arcs through new challenges",
                "- Raise stakes or complicate existing problems",
                "- Include character growth or revelation moments",
                "- Build toward upcoming climactic moments"
            ])
        
        return "\n".join(requirements)

    def _get_final_execution_instructions(self, target_word_count: int) -> str:
        """Final instructions for execution."""
        return f"""FINAL EXECUTION INSTRUCTIONS:

BEFORE YOU BEGIN WRITING:
1. Plan 4-6 distinct scenes or moments for this chapter
2. Identify the emotional arc - how do characters change?
3. Choose specific sensory details for each scene
4. Plan dialogue that reveals character and advances plot
5. Identify moments for internal character reflection

WHILE WRITING:
- Write in scenes, not summary
- Use active voice and concrete details
- Let characters drive the action through their choices
- Include conflict in every scene (external or internal)
- End each scene with momentum toward the next

WORD COUNT TRACKING:
- Aim for {target_word_count} words total
- Check progress every 500 words
- If falling short, add more scenes or expand existing ones
- If running long, tighten prose but maintain all required elements

QUALITY CHECKLIST:
- Does every paragraph advance the story?
- Are characters making meaningful choices?
- Is the dialogue authentic and purpose-driven?
- Have you avoided all forbidden phrases and patterns?
- Does the chapter end with compelling forward momentum?

NOW WRITE THE COMPLETE CHAPTER - {target_word_count} WORDS MINIMUM."""

    def _analyze_previous_chapters(self, previous_chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze previous chapters to identify patterns to avoid."""
        analysis = {
            "repetitive_phrases": [],
            "overused_words": [],
            "common_sentence_starts": [],
            "average_paragraph_length": 0
        }
        
        if not previous_chapters:
            return analysis
        
        # This would be enhanced with actual text analysis
        # For now, return basic structure
        return analysis

    def _select_narrative_devices(self, chapter_info: Dict[str, Any], story_context: Dict[str, Any]) -> List[str]:
        """Select appropriate narrative devices for this chapter."""
        devices = [
            "Use internal monologue to reveal character thoughts and motivations",
            "Employ environmental storytelling through setting details", 
            "Create tension through subtext in dialogue",
            "Use foreshadowing through seemingly casual details",
            "Show character relationships through their interactions and body language",
            "Include sensory details that ground readers in the scene",
            "Use pacing variation - mix action with reflection",
            "Create atmosphere through mood and tone consistency"
        ]
        
        # Select 4-6 devices for this chapter
        return random.sample(devices, min(6, len(devices)))

    def _load_anti_generic_database(self) -> Dict[str, List[str]]:
        """Load database of phrases and patterns to avoid."""
        return {
            "cliche_phrases": [
                "little did they know", "unbeknownst to", "time seemed to slow",
                "heart pounded", "blood ran cold", "breath caught", "world spun"
            ],
            "overused_starts": [
                "The morning was", "As the sun", "Meanwhile", "Suddenly", "Without warning"
            ],
            "generic_descriptions": [
                "piercing blue eyes", "raven black hair", "steely determination", 
                "icy cold stare", "warm smile", "gentle touch"
            ]
        }

    def _load_style_variations(self) -> Dict[str, List[str]]:
        """Load style variation options."""
        return {
            "sentence_starters": [
                "Despite", "Although", "Even as", "While", "Because", "Since", "Until"
            ],
            "transition_words": [
                "However", "Nevertheless", "Furthermore", "Additionally", "Consequently"
            ]
        }

    def _load_narrative_devices(self) -> List[str]:
        """Load available narrative devices."""
        return [
            "Stream of consciousness for character thoughts",
            "Dialogue that reveals subtext and hidden meanings",
            "Environmental details that reflect character emotions",
            "Flashbacks woven naturally into present action",
            "Multiple character perspectives within the chapter",
            "Symbolism through objects and settings",
            "Dramatic irony where readers know more than characters",
            "Parallel structure between different scenes or characters"
        ]

    def get_enhanced_outline_prompt(
        self,
        story_title: str,
        story_description: Optional[str],
        genre: Optional[str],
        target_chapters: int,
        context: Dict[str, Any]
    ) -> str:
        """Enhanced outline prompt that creates more sophisticated story structures."""
        return f"""ADVANCED NOVEL OUTLINE CREATION

Create a sophisticated {target_chapters}-chapter novel outline that demonstrates literary complexity and avoids predictable plot structures.

STORY FOUNDATION:
Title: {story_title}
{f"Premise: {story_description}" if story_description else ""}
{f"Genre: {genre}" if genre else ""}

OUTLINE SOPHISTICATION REQUIREMENTS:

1. MULTI-LAYERED NARRATIVE STRUCTURE:
   - Primary plot with 2-3 substantial subplots
   - Character arcs that intersect unexpectedly
   - Thematic threads woven throughout
   - Rising action that builds in complexity, not just intensity

2. CHARACTER-DRIVEN PLOT DEVELOPMENT:
   - Events arise from character choices and flaws
   - Each major character has distinct goals that conflict
   - Character relationships evolve and complicate throughout
   - Internal conflicts drive external action

3. AVOID PREDICTABLE STRUCTURES:
   - No "chosen one" or "fish out of water" unless subverted
   - Avoid convenient coincidences or deus ex machina solutions
   - Problems create new problems rather than simple escalation
   - Multiple valid interpretations of events and character motivations

4. CHAPTER DESIGN FOR SUBSTANTIAL CONTENT:
   - Each chapter should contain 2-4 distinct scenes
   - Minimum 2000-3000 words worth of content per chapter
   - Multiple character interactions per chapter
   - Balance of action, dialogue, character development, and description

FORMAT YOUR RESPONSE EXACTLY AS:

**NARRATIVE FOUNDATION**
Core Conflict: [The central tension driving the entire story]
Primary Theme: [Main thematic exploration]
Secondary Themes: [Supporting thematic elements]

**CHARACTER DYNAMICS**
[For each major character, describe their role, motivation, and how they change]

**ACT I: FOUNDATION** (Chapters 1-{target_chapters//3})
[Act summary focusing on character establishment and conflict initiation]

Chapter 1: [Title]
Content Overview: [2-3 detailed scenes this chapter will contain]
Character Focus: [Which characters are central and how they develop]
Plot Advancement: [Specific story elements that advance]
Estimated Length: 2500-3000 words

[Continue for all Act I chapters...]

**ACT II: DEVELOPMENT** (Chapters {target_chapters//3 + 1}-{target_chapters*2//3})
[Act summary focusing on complication and character growth]

[Continue chapter format...]

**ACT III: RESOLUTION** (Chapters {target_chapters*2//3 + 1}-{target_chapters})
[Act summary focusing on climax and resolution]

[Continue chapter format...]

**SUBPLOT INTEGRATION**
[Describe how subplots weave through and enhance the main narrative]

CRITICAL REQUIREMENTS:
- Every chapter must have substantial, scene-based content
- Character development must be central to plot progression  
- Avoid clichéd plot devices and predictable story beats
- Each chapter should justify 2500+ words of rich, detailed content
- Create a story that rewards re-reading with layered meanings"""

    def get_character_generation_prompt(
        self,
        story_context: Dict[str, Any],
        character_count: int = 5,
        complexity: str = "standard"
    ) -> str:
        """Enhanced character generation prompt for more realistic, complex characters."""
        return f"""ADVANCED CHARACTER DEVELOPMENT

Create {character_count} fully realized characters with psychological depth and authentic complexity. These characters must feel like real people with contradictions, flaws, and hidden depths.

STORY CONTEXT:
{self._format_story_context_for_characters(story_context)}

CHARACTER COMPLEXITY REQUIREMENTS:

1. PSYCHOLOGICAL REALISM:
   - Each character has contradictory traits that create internal conflict
   - Motivations are layered - surface wants vs. deeper needs
   - Past experiences inform present behavior in subtle ways
   - Characters surprise themselves with their reactions

2. AUTHENTIC DIALOGUE PATTERNS:
   - Distinct speech rhythms, vocabulary, and verbal tics
   - Characters speak around topics, not directly about them
   - Realistic interruptions, hesitations, and subtext
   - Speech patterns reflect background, education, and personality

3. RELATIONSHIP DYNAMICS:
   - Complex interpersonal chemistry and tension
   - Power dynamics that shift based on context
   - Shared history that influences current interactions
   - Competing loyalties and conflicting interests

4. BEHAVIORAL AUTHENTICITY:
   - Specific mannerisms and habits
   - Unconscious gestures that reveal character
   - Consistent decision-making patterns
   - Realistic responses to stress and conflict

FORMAT EACH CHARACTER EXACTLY AS:

**CHARACTER [Number]: [Full Name]**

*Core Identity:*
Role in Story: [Protagonist/Antagonist/Supporting - explain their function]
Age & Life Stage: [Age and what life phase they're navigating]
Core Contradiction: [The internal conflict that defines them]

*Psychological Profile:*
Surface Personality: [How they appear to others]
Hidden Depths: [What they hide or don't acknowledge about themselves]
Primary Fear: [What they're most afraid of, often unconscious]
Deepest Need: [What they truly need vs. what they think they want]
Fatal Flaw: [The character trait that creates problems for them]

*Background & Formation:*
Formative Experience: [Key past event that shaped their worldview]
Family Dynamics: [How their family relationships formed their patterns]
Education/Skills: [What they're good at and how they learned it]
Social Position: [Their place in society and how they feel about it]

*Behavioral Details:*
Speech Pattern: [How they talk - rhythm, vocabulary, verbal tics]
Physical Presence: [How they move, gesture, occupy space]
Stress Response: [How they behave under pressure]
Comfort Habits: [What they do when relaxed or seeking comfort]

*Relationship Dynamics:*
How They Love: [Their style in close relationships]
How They Fight: [Their conflict style and triggers]
Leadership Style: [How they behave when in charge]
When Vulnerable: [How they act when afraid or hurt]

*Story Integration:*
Character Arc: [How they change throughout the story]
Key Relationships: [Who they're most connected to and why]
Story Function: [How they serve the plot beyond their personal journey]
Unique Element: [Something unexpected or distinctive about them]

*Dialogue Sample:*
[2-3 lines of dialogue that capture their voice]

AUTHENTICITY REQUIREMENTS:
- No perfect heroes or pure villains
- Each character must have both admirable and frustrating qualities
- Characters should feel like they exist outside the story
- Include specific details that make them memorable
- Ensure each character could carry their own story
- Create characters whose actions surprise but make sense in hindsight"""

    def _format_story_context_for_characters(self, story_context: Dict[str, Any]) -> str:
        """Format story context specifically for character generation."""
        context_parts = []
        
        if "story" in story_context:
            story = story_context["story"]
            context_parts.extend([
                f"Title: {story.get('title', 'Untitled')}",
                f"Genre: {story.get('genre', 'Fiction')}"
            ])
            if story.get("description"):
                context_parts.append(f"Premise: {story['description']}")
        
        return "\n".join(context_parts)
