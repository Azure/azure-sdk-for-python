#!/usr/bin/env python3
"""
Simple validation test for Django auto-patching functionality.
"""
import sys
import os

# Add the package to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test that all our modules can be imported correctly."""
    print("Testing imports...")
    
    try:
        from azure.monitor.opentelemetry._web_snippet import WebSnippetConfig, WebSnippetInjector
        print("✅ Web snippet classes imported successfully")
    except Exception as e:
        print(f"❌ Failed to import web snippet classes: {e}")
        return False
    
    try:
        from azure.monitor.opentelemetry._configure import _setup_web_snippet, _patch_django_middleware
        print("✅ Configure functions imported successfully")
    except Exception as e:
        print(f"❌ Failed to import configure functions: {e}")
        return False
    
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        print("✅ Main configure function imported successfully")
    except Exception as e:
        print(f"❌ Failed to import main configure function: {e}")
        return False
    
    return True

def test_web_snippet_setup():
    """Test the web snippet setup function."""
    print("\nTesting web snippet setup...")
    
    try:
        from azure.monitor.opentelemetry._configure import _setup_web_snippet
        
        # Test with valid connection string
        config = {"connection_string": "InstrumentationKey=test;IngestionEndpoint=https://test.com/"}
        _setup_web_snippet(config)
        print("✅ Web snippet setup with connection string completed")
        
        # Test without connection string
        config = {}
        _setup_web_snippet(config)
        print("✅ Web snippet setup without connection string completed")
        
        return True
    except Exception as e:
        print(f"❌ Web snippet setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_django_patching_without_django():
    """Test Django patching when Django is not available."""
    print("\nTesting Django patching without Django...")
    
    try:
        from azure.monitor.opentelemetry._configure import _patch_django_middleware
        
        # This should not raise an exception even if Django is not available
        _patch_django_middleware("InstrumentationKey=test;IngestionEndpoint=https://test.com/")
        print("✅ Django patching handled gracefully without Django")
        
        return True
    except Exception as e:
        print(f"❌ Django patching failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration_types():
    """Test web snippet configuration types."""
    print("\nTesting configuration types...")
    
    try:
        from azure.monitor.opentelemetry._web_snippet import WebSnippetConfig
        
        # Test default config
        config = WebSnippetConfig()
        assert config.enabled == False
        assert config.connection_string is None
        print("✅ Default configuration works")
        
        # Test custom config
        config = WebSnippetConfig(
            enabled=True,
            connection_string="InstrumentationKey=test;IngestionEndpoint=https://test.com/"
        )
        assert config.enabled == True
        assert config.connection_string == "InstrumentationKey=test;IngestionEndpoint=https://test.com/"
        
        # Test to_dict conversion
        config_dict = config.to_dict()
        assert "enabled" in config_dict
        assert "connectionString" in config_dict
        print("✅ Custom configuration works")
        
        return True
    except Exception as e:
        print(f"❌ Configuration types test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all validation tests."""
    print("🧪 Azure Monitor OpenTelemetry - Django Auto-Patching Validation")
    print("=" * 70)
    
    tests = [
        test_imports,
        test_web_snippet_setup,
        test_django_patching_without_django,
        test_configuration_types,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("Test failed!")
        except Exception as e:
            print(f"Test crashed: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Django auto-patching implementation is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
