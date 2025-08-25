#!/usr/bin/env python3
"""
Simple syntax and import test for the web snippet implementation.
"""
import sys
import os
import ast

def test_python_syntax():
    """Test that all our Python files have valid syntax."""
    print("Testing Python syntax...")
    
    files_to_check = [
        "azure/monitor/opentelemetry/_web_snippet/_config.py",
        "azure/monitor/opentelemetry/_web_snippet/_snippet_injector.py", 
        "azure/monitor/opentelemetry/_web_snippet/_django_middleware.py",
        "azure/monitor/opentelemetry/_web_snippet/__init__.py",
        "azure/monitor/opentelemetry/__init__.py",
    ]
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the file to check for syntax errors
            ast.parse(content)
            print(f"✅ {file_path} - Valid syntax")
        except SyntaxError as e:
            print(f"❌ {file_path} - Syntax error: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ {file_path} - File not found")
            return False
        except Exception as e:
            print(f"❌ {file_path} - Error: {e}")
            return False
    
    return True

def test_configure_file_changes():
    """Test that _configure.py has our new functions."""
    print("\nTesting _configure.py changes...")
    
    try:
        with open("azure/monitor/opentelemetry/_configure.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for our new functions
        required_functions = [
            "_setup_web_snippet",
            "_patch_django_middleware"
        ]
        
        for func_name in required_functions:
            if f"def {func_name}" in content:
                print(f"✅ Function {func_name} found")
            else:
                print(f"❌ Function {func_name} NOT found")
                return False
        
        # Check that configure_azure_monitor calls the new function
        if "_setup_web_snippet(configurations)" in content:
            print("✅ configure_azure_monitor calls _setup_web_snippet")
        else:
            print("❌ configure_azure_monitor does NOT call _setup_web_snippet")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error checking _configure.py: {e}")
        return False

def test_exports():
    """Test that the exports are configured correctly."""
    print("\nTesting exports...")
    
    try:
        # Check main __init__.py
        with open("azure/monitor/opentelemetry/__init__.py", 'r', encoding='utf-8') as f:
            main_init = f.read()
        
        if 'DjangoWebSnippetMiddleware' not in main_init:
            print("✅ DjangoWebSnippetMiddleware correctly removed from main exports")
        else:
            print("❌ DjangoWebSnippetMiddleware still exported in main __init__.py")
            return False
        
        # Check web snippet __init__.py
        with open("azure/monitor/opentelemetry/_web_snippet/__init__.py", 'r', encoding='utf-8') as f:
            snippet_init = f.read()
        
        if 'from ._django_middleware import DjangoWebSnippetMiddleware' in snippet_init:
            print("✅ DjangoWebSnippetMiddleware imported in _web_snippet __init__.py")
        else:
            print("❌ DjangoWebSnippetMiddleware NOT imported in _web_snippet __init__.py")
            return False
        
        if 'DjangoWebSnippetMiddleware' not in snippet_init.split('__all__')[1]:
            print("✅ DjangoWebSnippetMiddleware correctly not in __all__")
        else:
            print("❌ DjangoWebSnippetMiddleware incorrectly in __all__")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error checking exports: {e}")
        return False

def test_file_structure():
    """Test that all expected files exist."""
    print("\nTesting file structure...")
    
    expected_files = [
        "azure/monitor/opentelemetry/_web_snippet/__init__.py",
        "azure/monitor/opentelemetry/_web_snippet/_config.py",
        "azure/monitor/opentelemetry/_web_snippet/_snippet_injector.py",
        "azure/monitor/opentelemetry/_web_snippet/_django_middleware.py",
        "azure/monitor/opentelemetry/__init__.py",
        "azure/monitor/opentelemetry/_configure.py",
        "tests/test_configure.py",
        "tests/test_web_snippet.py",
    ]
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Azure Monitor OpenTelemetry - Implementation Structure Test")
    print("=" * 70)
    
    # Change to the package directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    tests = [
        test_file_structure,
        test_python_syntax,
        test_configure_file_changes,
        test_exports,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Test crashed: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All structure tests passed! Implementation looks good.")
        print("\n📝 Summary of changes:")
        print("  ✅ Django middleware auto-patching implemented")
        print("  ✅ _setup_web_snippet function added to _configure.py")
        print("  ✅ configure_azure_monitor updated to call web snippet setup")
        print("  ✅ DjangoWebSnippetMiddleware removed from public exports")
        print("  ✅ All Python files have valid syntax")
        print("\n🚀 The implementation is ready for testing with a Django application!")
        return True
    else:
        print("❌ Some structure tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
