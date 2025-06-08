    def _parse_characters_enhanced(self, characters_text: str, story_id: int) -> List[Dict[str, Any]]:
        """Parse AI-generated character descriptions with enhanced fields."""
        characters = []
        current_character = None

        lines = characters_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for character names (usually start with number or bullet)
            name_match = re.match(r'(?:[0-9]+\.|CHARACTER [0-9]+:|\*|\-)\s*([^:]+)(?::|$)', line, re.IGNORECASE)
            if name_match:
                if current_character:
                    characters.append(current_character)

                current_character = {
                    "name": name_match.group(1).strip(),
                    "role": "",
                    "profile": "",
                    "personality": "",
                    "traits": {},
                    "arc": "",
                    "speech_pattern": "",
                    "background": "",
                    "motivations": "",
                    "internal_conflict": ""
                }
                continue

            # Parse enhanced character fields
            if current_character and line:
                line_lower = line.lower()
                if "role:" in line_lower or "role in story:" in line_lower:
                    current_character["role"] = line.split(":", 1)[1].strip()
                elif "speech pattern:" in line_lower or "speech:" in line_lower:
                    current_character["speech_pattern"] = line.split(":", 1)[1].strip()
                elif "personality:" in line_lower:
                    current_character["personality"] = line.split(":", 1)[1].strip()
                elif "background:" in line_lower:
                    current_character["background"] = line.split(":", 1)[1].strip()
                elif "motivations:" in line_lower or "motivation:" in line_lower:
                    current_character["motivations"] = line.split(":", 1)[1].strip()
                elif "internal conflict:" in line_lower or "core contradiction:" in line_lower:
                    current_character["internal_conflict"] = line.split(":", 1)[1].strip()
                elif "character arc:" in line_lower or "arc:" in line_lower:
                    current_character["arc"] = line.split(":", 1)[1].strip()
                elif "age:" in line_lower:
                    current_character["traits"]["age"] = line.split(":", 1)[1].strip()
                elif "appearance:" in line_lower:
                    current_character["traits"]["appearance"] = line.split(":", 1)[1].strip()
                elif "skills:" in line_lower or "talents:" in line_lower:
                    current_character["traits"]["skills"] = line.split(":", 1)[1].strip()
                elif "relationships:" in line_lower:
                    current_character["traits"]["relationships"] = line.split(":", 1)[1].strip()
                elif "unique element:" in line_lower:
                    current_character["traits"]["unique_element"] = line.split(":", 1)[1].strip()
                else:
                    # Add to profile if no specific field matches
                    if current_character["profile"]:
                        current_character["profile"] += " " + line
                    else:
                        current_character["profile"] = line

        # Add the last character
        if current_character:
            characters.append(current_character)

        return characters

    def _parse_world_elements_enhanced(self, world_text: str, story_id: int) -> List[Dict[str, Any]]:
        """Parse AI-generated world building elements with enhanced fields."""
        world_elements = []
        current_element = None

        lines = world_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for element names (usually start with number or bullet)
            name_match = re.match(r'(?:[0-9]+\.|ELEMENT [0-9]+:|\*|\-)\s*([^:]+)(?::|$)', line, re.IGNORECASE)
            if name_match:
                if current_element:
                    world_elements.append(current_element)

                current_element = {
                    "name": name_match.group(1).strip(),
                    "type": "Location",
                    "description": "",
                    "significance": "",
                    "details": {},
                    "cultural_impact": "",
                    "story_integration": ""
                }
                continue

            # Parse enhanced world element fields
            if current_element and line:
                line_lower = line.lower()
                if "type:" in line_lower:
                    current_element["type"] = line.split(":", 1)[1].strip()
                elif "description:" in line_lower:
                    current_element["description"] = line.split(":", 1)[1].strip()
                elif "significance:" in line_lower:
                    current_element["significance"] = line.split(":", 1)[1].strip()
                elif "cultural impact:" in line_lower:
                    current_element["cultural_impact"] = line.split(":", 1)[1].strip()
                elif "story integration:" in line_lower or "story impact:" in line_lower:
                    current_element["story_integration"] = line.split(":", 1)[1].strip()
                elif "details:" in line_lower:
                    current_element["details"]["info"] = line.split(":", 1)[1].strip()
                else:
                    # Add to description if no specific field matches
                    if current_element["description"]:
                        current_element["description"] += " " + line
                    else:
                        current_element["description"] = line

        # Add the last element
        if current_element:
            world_elements.append(current_element)

        return world_elements

    def _build_enhanced_editing_prompt(
        self, 
        original_text: str, 
        instruction: str, 
        focus_area: str, 
        context: str, 
        maintain_length: bool
    ) -> str:
        """Build enhanced editing prompt with specific focus areas."""
        length_instruction = ""
        if maintain_length:
            word_count = len(original_text.split())
            length_instruction = f"MAINTAIN APPROXIMATELY {word_count} WORDS - do not significantly shorten or expand the text."
        else:
            length_instruction = "Adjust length as needed to improve quality."

        focus_instructions = {
            "dialogue": [
                "- Make dialogue more authentic and character-specific",
                "- Add subtext and realistic speech patterns", 
                "- Include natural interruptions and hesitations",
                "- Ensure each character has a distinct voice"
            ],
            "description": [
                "- Enhance sensory details and atmospheric descriptions",
                "- Use more specific, concrete imagery",
                "- Create vivid mental pictures without purple prose",
                "- Balance description with action and dialogue"
            ],
            "pacing": [
                "- Improve rhythm and flow between scenes",
                "- Vary sentence structure for better pacing",
                "- Balance action, reflection, and dialogue",
                "- Ensure smooth transitions between moments"
            ],
            "character": [
                "- Deepen character psychology and motivations",
                "- Show character emotions through actions",
                "- Develop character relationships and dynamics",
                "- Add authentic character reactions and growth"
            ],
            "prose": [
                "- Elevate language sophistication and style",
                "- Improve sentence variety and structure",
                "- Eliminate weak or generic phrasing",
                "- Enhance literary quality while maintaining clarity"
            ],
            "overall": [
                "- Improve all aspects of the writing simultaneously",
                "- Focus on clarity, engagement, and quality",
                "- Enhance both style and substance",
                "- Create more compelling and polished prose"
            ]
        }

        selected_instructions = focus_instructions.get(focus_area, focus_instructions["overall"])

        return f"""ADVANCED TEXT EDITING WITH FOCUS ON {focus_area.upper()}

EDITING INSTRUCTION: {instruction}

FOCUS AREA REQUIREMENTS:
{chr(10).join(selected_instructions)}

LENGTH REQUIREMENT: {length_instruction}

QUALITY STANDARDS:
- Eliminate any AI-sounding phrases or clichés
- Ensure every sentence serves a clear purpose
- Maintain narrative consistency and flow
- Use sophisticated but accessible language
- Create engaging, human-like prose

CONTEXT: {context}

ORIGINAL TEXT TO EDIT:
---
{original_text}
---

EDITED VERSION:
Provide the improved version that addresses the instruction while maintaining the core meaning and narrative flow. Focus specifically on {focus_area} improvements."""

    def _build_sophistication_prompt(
        self, 
        original_text: str, 
        focus_area: str, 
        target_length: str, 
        style_target: str
    ) -> str:
        """Build sophistication enhancement prompt with style targets."""
        length_instructions = {
            "shorten": "Create a more concise version that maintains all essential meaning",
            "maintain": "Keep approximately the same length while improving quality",
            "expand": "Expand with rich detail and enhanced development"
        }

        style_instructions = {
            "accessible": [
                "- Use clear, readable language accessible to general audiences",
                "- Maintain engaging storytelling without complexity for its own sake",
                "- Focus on clarity and emotional connection"
            ],
            "literary": [
                "- Employ sophisticated prose techniques and elevated language",
                "- Use complex sentence structures and rich vocabulary",
                "- Create layered meaning and subtle artistry"
            ],
            "commercial": [
                "- Write engaging, page-turning prose that hooks readers",
                "- Balance sophistication with broad appeal",
                "- Focus on strong pacing and compelling storytelling"
            ],
            "experimental": [
                "- Push creative boundaries with innovative techniques",
                "- Experiment with structure, voice, and style",
                "- Challenge conventional narrative approaches"
            ]
        }

        return f"""ADVANCED TEXT SOPHISTICATION ENHANCEMENT

TARGET STYLE: {style_target.upper()}
TARGET LENGTH: {target_length.upper()}
FOCUS AREA: {focus_area.upper()}

STYLE REQUIREMENTS:
{chr(10).join(style_instructions[style_target])}

LENGTH INSTRUCTION: {length_instructions[target_length]}

SOPHISTICATION GOALS:
- Elevate prose quality while maintaining authenticity
- Eliminate generic or AI-typical phrasing
- Enhance rhythm, flow, and linguistic precision
- Create more engaging and memorable prose
- Develop distinctive voice and style

ORIGINAL TEXT:
---
{original_text}
---

ENHANCED VERSION:
Provide the sophisticated version that demonstrates elevated writing craft while targeting {style_target} style."""

# Add these methods to the enhanced_generation_service.py file
