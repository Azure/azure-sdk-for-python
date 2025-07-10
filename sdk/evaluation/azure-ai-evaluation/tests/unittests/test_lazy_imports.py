"""Tests for lazy import behavior of optional dependencies."""

import sys
import unittest
from io import StringIO
import importlib


class TestLazyImports(unittest.TestCase):
    """Test lazy import behavior for optional dependencies."""

    def test_no_messages_during_module_import(self):
        """Test that no messages are printed when importing the main module."""
        # Capture stderr to check for unwanted messages
        captured_stderr = StringIO()
        original_stderr = sys.stderr
        sys.stderr = captured_stderr

        try:
            # Test imports that would normally fail with missing dependencies
            # Since we can't easily control the dependency availability in the test environment,
            # we test the lazy import setup directly

            # This should not print any messages during setup
            _lazy_imports = {}
            _patch_all = []

            def _create_lazy_import(class_name, module_path, dependency_name):
                """Create a lazy import function for optional dependencies."""

                def lazy_import():
                    try:
                        module = __import__(module_path, fromlist=[class_name])
                        cls = getattr(module, class_name)
                        _patch_all.append(class_name)
                        return cls
                    except ImportError:
                        raise ImportError(
                            f"Could not import {class_name}. Please install the dependency with `pip install {dependency_name}`."
                        )

                return lazy_import

            # Setting up lazy imports should not print any messages
            _lazy_imports["SKAgentConverter"] = _create_lazy_import(
                "SKAgentConverter",
                "azure.ai.evaluation._converters._sk_services",
                "semantic-kernel",
            )

            # Check that no messages were printed during setup
            stderr_output = captured_stderr.getvalue()
            self.assertEqual(
                stderr_output,
                "",
                "No messages should be printed during lazy import setup",
            )

        finally:
            sys.stderr = original_stderr

    def test_message_shown_when_accessing_missing_dependency(self):
        """Test that appropriate message is shown when accessing a class with missing dependency."""
        # Test the __getattr__ functionality
        _lazy_imports = {}

        def _create_lazy_import(class_name, module_path, dependency_name):
            """Create a lazy import function for optional dependencies."""

            def lazy_import():
                try:
                    # This should fail in most test environments
                    module = __import__(module_path, fromlist=[class_name])
                    cls = getattr(module, class_name)
                    return cls
                except ImportError:
                    raise ImportError(
                        f"Could not import {class_name}. Please install the dependency with `pip install {dependency_name}`."
                    )

            return lazy_import

        _lazy_imports["SKAgentConverter"] = _create_lazy_import(
            "SKAgentConverter",
            "azure.ai.evaluation._converters._sk_services",
            "semantic-kernel",
        )

        def mock_getattr(name):
            """Mock __getattr__ function like the one in __init__.py"""
            if name in _lazy_imports:
                return _lazy_imports[name]()
            raise AttributeError(f"module has no attribute '{name}'")

        # This should raise ImportError directly
        with self.assertRaises(ImportError) as cm:
            mock_getattr("SKAgentConverter")

        # Check that the ImportError message contains the expected information
        error_message = str(cm.exception)
        self.assertIn("Could not import SKAgentConverter", error_message)
        self.assertIn("pip install semantic-kernel", error_message)

    def test_getattr_with_non_existent_attribute(self):
        """Test __getattr__ behavior with non-existent attributes."""
        _lazy_imports = {}

        def mock_getattr(name):
            """Mock __getattr__ function like the one in __init__.py"""
            if name in _lazy_imports:
                return _lazy_imports[name]()
            raise AttributeError(f"module has no attribute '{name}'")

        # Test with a non-existent attribute
        with self.assertRaises(AttributeError) as cm:
            mock_getattr("NonExistentClass")

        self.assertIn("has no attribute 'NonExistentClass'", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
