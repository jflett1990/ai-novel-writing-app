    def get_enhanced_world_building_prompt(
        self,
        story_context: Dict[str, Any],
        element_count: int = 8,
        complexity_focus: str = "balanced",
        complexity: str = "standard"
    ) -> str:
        """
        Enhanced world building prompt with focus areas and sophistication.
        """
        # Get complexity-specific world building instructions
        world_complexity = self._get_world_complexity_instructions(complexity)
        
        # Get focus-specific instructions
        focus_instructions = self._get_focus_specific_instructions(complexity_focus)

        prompt_parts = [
            f"ADVANCED WORLD BUILDING - FOCUS: {complexity_focus.upper()}",
            "",
            f"Create {element_count} richly detailed world elements that demonstrate sophisticated world-building craft. Each element must feel authentic, purposeful, and seamlessly integrated into the narrative fabric. Avoid fantasy/sci-fi clichés and generic world-building tropes.",
            "",
            f"COMPLEXITY LEVEL: {complexity.upper()}",
            *world_complexity,
            "",
            "FOCUS AREA REQUIREMENTS:",
            *focus_instructions,
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
            "WORLD BUILDING SOPHISTICATION REQUIREMENTS:",
            "- Create original, unexpected elements that avoid common tropes",
            "- Ensure each element has cultural, historical, or narrative significance", 
            "- Include specific details that make elements feel lived-in and authentic",
            "- Show how elements influence character behavior and story development",
            "- Create interconnections between different world elements",
            "- Ground fantastical elements in logical internal consistency",
            "",
            "ELEMENT TYPES TO INCLUDE (mix these):",
            "- Unique locations with specific cultural significance",
            "- Organizations with complex internal dynamics", 
            "- Cultural practices that reveal societal values",
            "- Historical events that shaped the current world",
            "- Technologies or systems with unintended consequences",
            "- Social structures that create interesting conflicts",
            "",
            "FORMAT EACH ELEMENT AS:",
            "",
            "**ELEMENT [Number]: [Element Name]**",
            "*Type:* [Location/Organization/Culture/Technology/History/Custom]",
            "*Description:* [Rich, specific description with concrete details]",
            "*Cultural Impact:* [How this shapes society, behavior, or beliefs]",
            "*Story Integration:* [How this affects characters and plot development]", 
            "*Unique Aspects:* [What makes this distinctive and memorable]",
            "*Interconnections:* [How it relates to other world elements]",
            "",
            f"Create exactly {element_count} world elements that feel authentic, purposeful, and interconnected."
        ])

        return "\n".join(prompt_parts)

    def _get_focus_specific_instructions(self, complexity_focus: str) -> List[str]:
        """Get instructions specific to the world building focus area."""
        focus_map = {
            "cultural": [
                "- Emphasize unique social customs, traditions, and belief systems",
                "- Create distinctive languages, art forms, or cultural practices",
                "- Show how cultural elements influence character worldviews",
                "- Include cultural conflicts and generational differences"
            ],
            "political": [
                "- Develop complex governmental and power structures",
                "- Create political factions with competing interests",
                "- Show how political systems affect daily life",
                "- Include political intrigue and power dynamics"
            ],
            "environmental": [
                "- Focus on unique geographical features and their effects",
                "- Create distinctive climates, ecosystems, or natural phenomena",
                "- Show how environment shapes culture and character",
                "- Include environmental challenges and adaptations"
            ],
            "magical": [
                "- Develop consistent magical or supernatural systems",
                "- Create unique magical traditions and limitations",
                "- Show societal impact of magical elements",
                "- Include magical conflicts and consequences"
            ],
            "technological": [
                "- Create distinctive technologies and their social impact",
                "- Show how technology changes social structures",
                "- Include technological conflicts and unintended effects",
                "- Develop unique technological traditions"
            ],
            "balanced": [
                "- Create a mix of cultural, political, and environmental elements",
                "- Ensure all elements feel interconnected and purposeful",
                "- Balance different types of world-building aspects",
                "- Show how various elements influence each other"
            ]
        }
        
        return focus_map.get(complexity_focus, focus_map["balanced"])

# Add this method to the enhanced_prompt_templates.py file
