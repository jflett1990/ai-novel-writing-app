"""Basic test to verify the backend setup works."""

import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all core modules can be imported."""

    # Test core imports
    from core.config import settings  # noqa: F401
    print("✓ Core config imported successfully")

    # Test model imports
    from models import Chapter, Character, Story, WorldElement  # noqa: F401
    print("✓ Models imported successfully")

    # Test schema imports
    from schemas.story import StoryCreate, StoryResponse  # noqa: F401
    print("✓ Schemas imported successfully")

    # Test service imports (these might fail if optional dependencies aren't installed)
    try:
        from services.ai_providers import create_ai_provider  # noqa: F401
        print("✓ AI providers imported successfully")
    except ImportError as exc:  # pragma: no cover - informational output
        print(f"⚠ AI providers import failed (expected if dependencies not installed): {exc}")

    try:
        from services.context_service import ContextService  # noqa: F401
        print("✓ Context service imported successfully")
    except ImportError as exc:  # pragma: no cover - informational output
        print(f"⚠ Context service import failed: {exc}")

    print("\n✅ Basic imports test passed!")


def test_config():
    """Test configuration loading."""

    from core.config import settings

    print(f"Project name: {settings.project_name}")
    print(f"API prefix: {settings.api_v1_prefix}")
    print(f"AI provider: {settings.ai_provider}")
    print(f"Debug mode: {settings.debug}")

    assert settings.project_name
    assert settings.api_v1_prefix.startswith("/")
    assert settings.ai_provider in {"copilot", "openai", "ollama"}

    print("\n✅ Configuration test passed!")


def test_database_models():
    """Test that database models are properly defined."""

    from models.chapter import Chapter
    from models.character import Character
    from models.story import Act, Story
    from models.world_element import WorldElement

    # Test that models have expected attributes
    assert hasattr(Story, "story_id")
    assert hasattr(Story, "title")
    assert hasattr(Character, "character_id")
    assert hasattr(Character, "name")
    assert hasattr(WorldElement, "element_id")
    assert hasattr(WorldElement, "type")
    assert hasattr(Chapter, "chapter_id")
    assert hasattr(Chapter, "content")
    assert hasattr(Act, "act_id")

    print("✅ Database models test passed!")


def main():
    """Run all basic tests."""

    print("🧪 Running basic backend tests...\n")

    tests = [
        test_imports,
        test_config,
        test_database_models,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
        except AssertionError as exc:
            print(f"❌ {test.__name__} failed: {exc}")
        except Exception as exc:  # pragma: no cover - command line helper
            print(f"❌ {test.__name__} raised an unexpected error: {exc}")
        else:
            passed += 1
        print()

    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All basic tests passed! The backend setup looks good.")
        return True

    print("⚠️  Some tests failed. Check the output above for details.")
    return False


if __name__ == "__main__":  # pragma: no cover - command line helper
    success = main()
    sys.exit(0 if success else 1)
