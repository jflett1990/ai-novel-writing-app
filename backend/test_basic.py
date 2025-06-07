"""
Basic test to verify the backend setup works.
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all core modules can be imported."""
    try:
        # Test core imports
        from core.config import settings
        print("✓ Core config imported successfully")
        
        # Test model imports
        from models import Story, Character, WorldElement, Chapter
        print("✓ Models imported successfully")
        
        # Test schema imports
        from schemas.story import StoryCreate, StoryResponse
        print("✓ Schemas imported successfully")
        
        # Test service imports (these might fail if dependencies aren't installed)
        try:
            from services.ai_providers import create_ai_provider
            print("✓ AI providers imported successfully")
        except ImportError as e:
            print(f"⚠ AI providers import failed (expected if dependencies not installed): {e}")
        
        try:
            from services.context_service import ContextService
            print("✓ Context service imported successfully")
        except ImportError as e:
            print(f"⚠ Context service import failed: {e}")
        
        print("\n✅ Basic imports test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False


def test_config():
    """Test configuration loading."""
    try:
        from core.config import settings
        
        print(f"Project name: {settings.project_name}")
        print(f"API prefix: {settings.api_v1_prefix}")
        print(f"AI provider: {settings.ai_provider}")
        print(f"Debug mode: {settings.debug}")
        
        print("\n✅ Configuration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_database_models():
    """Test that database models are properly defined."""
    try:
        from models.story import Story, Act
        from models.chapter import Chapter
        from models.character import Character
        from models.world_element import WorldElement
        
        # Test that models have expected attributes
        assert hasattr(Story, 'story_id')
        assert hasattr(Story, 'title')
        assert hasattr(Character, 'character_id')
        assert hasattr(Character, 'name')
        assert hasattr(WorldElement, 'element_id')
        assert hasattr(WorldElement, 'type')
        assert hasattr(Chapter, 'chapter_id')
        assert hasattr(Chapter, 'content')
        
        print("✅ Database models test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False


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
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! The backend setup looks good.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
