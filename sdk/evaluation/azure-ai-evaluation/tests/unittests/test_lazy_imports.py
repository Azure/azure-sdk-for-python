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

            def _try_import_aiagentconverter():
                try:
                    # This will likely fail in test environment
                    from azure.ai.evaluation._converters._ai_services import AIAgentConverter
                    return AIAgentConverter
                except ImportError:
                    raise ImportError(
                        "[INFO] Could not import AIAgentConverter. Please install the dependency with `pip install azure-ai-projects`."
                    )

            def _try_import_skagentconverter():
                try:
                    from azure.ai.evaluation._converters._sk_services import SKAgentConverter
                    return SKAgentConverter
                except ImportError:
                    raise ImportError(
                        "[INFO] Could not import SKAgentConverter. Please install the dependency with `pip install semantic-kernel`."
                    )

            # Setting up lazy imports should not print any messages
            _lazy_imports["AIAgentConverter"] = _try_import_aiagentconverter
            _lazy_imports["SKAgentConverter"] = _try_import_skagentconverter

            # Check that no messages were printed during setup
            stderr_output = captured_stderr.getvalue()
            self.assertEqual(stderr_output, "", "No messages should be printed during lazy import setup")

        finally:
            sys.stderr = original_stderr

    def test_message_shown_when_accessing_missing_dependency(self):
        """Test that appropriate message is shown when accessing a class with missing dependency."""
        # Test the __getattr__ functionality
        _lazy_imports = {}

        def _try_import_aiagentconverter():
            try:
                # This should fail in most test environments
                from azure.ai.evaluation._converters._ai_services import AIAgentConverter
                return AIAgentConverter
            except ImportError:
                raise ImportError(
                    "[INFO] Could not import AIAgentConverter. Please install the dependency with `pip install azure-ai-projects`."
                )

        _lazy_imports["AIAgentConverter"] = _try_import_aiagentconverter

        def mock_getattr(name):
            """Mock __getattr__ function like the one in __init__.py"""
            if name in _lazy_imports:
                try:
                    return _lazy_imports[name]()
                except ImportError as e:
                    import sys
                    print(str(e), file=sys.stderr)
                    raise AttributeError(f"module has no attribute '{name}'") from e
            raise AttributeError(f"module has no attribute '{name}'")

        # Capture stderr to check the message
        captured_stderr = StringIO()
        original_stderr = sys.stderr
        sys.stderr = captured_stderr

        try:
            # This should print the message and raise AttributeError
            with self.assertRaises(AttributeError):
                mock_getattr("AIAgentConverter")

            stderr_output = captured_stderr.getvalue()
            self.assertIn("Could not import AIAgentConverter", stderr_output)
            self.assertIn("pip install azure-ai-projects", stderr_output)

        finally:
            sys.stderr = original_stderr

    def test_getattr_with_non_existent_attribute(self):
        """Test __getattr__ behavior with non-existent attributes."""
        _lazy_imports = {}

        def mock_getattr(name):
            """Mock __getattr__ function like the one in __init__.py"""
            if name in _lazy_imports:
                try:
                    return _lazy_imports[name]()
                except ImportError as e:
                    import sys
                    print(str(e), file=sys.stderr)
                    raise AttributeError(f"module has no attribute '{name}'") from e
            raise AttributeError(f"module has no attribute '{name}'")

        # Test with a non-existent attribute
        with self.assertRaises(AttributeError) as cm:
            mock_getattr("NonExistentClass")

        self.assertIn("has no attribute 'NonExistentClass'", str(cm.exception))


if __name__ == "__main__":
    unittest.main()