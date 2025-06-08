#!/usr/bin/env python3
"""
Test script to verify that outline generation properly includes character context.
This test validates the fix for the issue where outline generation was ignoring
character information from the story context.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.prompt_templates import PromptTemplates


def test_outline_prompt_includes_characters():
    """Test that outline generation prompt includes character information."""
    
    # Create test story context with characters
    story_context = {
        "story": {
            "title": "The Shadow's Edge",
            "description": "A tale of redemption and betrayal in a world of magic",
            "genre": "Fantasy"
        },
        "characters": [
            {
                "name": "Elena Blackthorne",
                "role": "protagonist",
                "personality": "Determined but haunted by past mistakes",
                "motivations": "Seeks to redeem herself for a terrible betrayal",
                "arc": "From guilt-ridden exile to reluctant hero"
            },
            {
                "name": "Marcus Veil",
                "role": "antagonist", 
                "personality": "Charismatic but ruthlessly ambitious",
                "motivations": "Wants to reshape the world according to his vision",
                "arc": "From trusted ally to corrupted enemy"
            },
            {
                "name": "Kira Stormwind",
                "role": "supporting character",
                "personality": "Loyal and brave but impulsive",
                "motivations": "Protect her friends and homeland",
                "arc": "Learns the value of patience and strategy"
            }
        ],
        "world_elements": {
            "locations": [
                {
                    "name": "The Shattered Citadel",
                    "description": "Ancient fortress where the great betrayal occurred"
                }
            ],
            "organizations": [
                {
                    "name": "The Order of Shadows",
                    "description": "Secret society that manipulates events from behind the scenes"
                }
            ]
        },
        "outline": [
            {
                "number": 1,
                "title": "The Return",
                "summary": "Elena returns to her homeland after years of exile"
            }
        ]
    }
    
    # Generate outline prompt
    prompt_templates = PromptTemplates()
    prompt = prompt_templates.get_outline_prompt(
        story_title="The Shadow's Edge",
        story_description="A tale of redemption and betrayal in a world of magic",
        genre="Fantasy",
        target_chapters=15,
        context=story_context
    )
    
    print("=== OUTLINE PROMPT TEST ===")
    print("Testing that outline generation includes character context...\n")
    
    # Check that character information is included
    character_checks = [
        ("Elena Blackthorne", "Elena Blackthorne" in prompt),
        ("Marcus Veil", "Marcus Veil" in prompt),
        ("Kira Stormwind", "Kira Stormwind" in prompt),
        ("protagonist", "protagonist" in prompt),
        ("antagonist", "antagonist" in prompt),
        ("Character motivations", "Seeks to redeem herself" in prompt),
        ("Character arcs", "From guilt-ridden exile" in prompt),
    ]
    
    # Check that world elements are included
    world_checks = [
        ("World elements section", "WORLD/SETTING ELEMENTS" in prompt),
        ("Shattered Citadel", "Shattered Citadel" in prompt),
        ("Order of Shadows", "Order of Shadows" in prompt),
    ]
    
    # Check that existing outline is included
    outline_checks = [
        ("Existing chapters section", "EXISTING CHAPTERS" in prompt),
        ("Chapter 1 reference", "Chapter 1: The Return" in prompt),
    ]
    
    # Check that character-focused requirements are included
    requirement_checks = [
        ("Character development focus", "Character arcs that develop naturally through the story" in prompt),
        ("Character motivation integration", "character motivations into plot" in prompt),
        ("Character involvement", "each character has meaningful involvement" in prompt),
    ]
    
    print("CHARACTER INTEGRATION CHECKS:")
    all_passed = True
    for check_name, result in character_checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not result:
            all_passed = False
    
    print("\nWORLD ELEMENT INTEGRATION CHECKS:")
    for check_name, result in world_checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not result:
            all_passed = False
    
    print("\nEXISTING OUTLINE INTEGRATION CHECKS:")
    for check_name, result in outline_checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not result:
            all_passed = False
    
    print("\nCHARACTER-FOCUSED REQUIREMENT CHECKS:")
    for check_name, result in requirement_checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not result:
            all_passed = False
    
    print(f"\n=== OVERALL RESULT ===")
    if all_passed:
        print("✅ ALL TESTS PASSED: Outline generation now properly includes character context!")
    else:
        print("❌ SOME TESTS FAILED: Character integration may not be working correctly.")
    
    print(f"\n=== SAMPLE PROMPT OUTPUT ===")
    print("First 1000 characters of generated prompt:")
    print("-" * 50)
    print(prompt[:1000])
    print("-" * 50)
    
    return all_passed


def test_outline_prompt_without_characters():
    """Test that outline generation works when no characters are provided."""
    
    # Create test story context without characters
    story_context = {
        "story": {
            "title": "Empty Story",
            "description": "A story with no characters yet",
            "genre": "Mystery"
        },
        "characters": [],
        "world_elements": {},
        "outline": []
    }
    
    prompt_templates = PromptTemplates()
    prompt = prompt_templates.get_outline_prompt(
        story_title="Empty Story",
        story_description="A story with no characters yet",
        genre="Mystery",
        target_chapters=10,
        context=story_context
    )
    
    print("\n=== EMPTY CONTEXT TEST ===")
    print("Testing outline generation with no characters...")
    
    # Should not crash and should still generate a valid prompt
    basic_checks = [
        ("Contains story title", "Empty Story" in prompt),
        ("Contains genre", "Mystery" in prompt),
        ("Contains target chapters", "10 chapters" in prompt),
        ("Contains format instructions", "FORMAT YOUR RESPONSE" in prompt),
    ]
    
    all_passed = True
    for check_name, result in basic_checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("✅ Empty context test passed: Outline generation handles missing characters gracefully")
    else:
        print("❌ Empty context test failed")
    
    return all_passed


if __name__ == "__main__":
    print("Testing outline generation character integration fix...\n")
    
    test1_passed = test_outline_prompt_includes_characters()
    test2_passed = test_outline_prompt_without_characters()
    
    print(f"\n{'='*60}")
    print("FINAL TEST SUMMARY:")
    print(f"Character Integration Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Empty Context Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! The outline generation fix is working correctly.")
        print("Characters, world elements, and existing outline data are now properly")
        print("integrated into outline generation prompts.")
    else:
        print("\n⚠️  Some tests failed. Please review the implementation.")
    
    print(f"{'='*60}")
