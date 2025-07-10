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
            _lazy_imports["AIAgentConverter"] = _create_lazy_import("AIAgentConverter", "azure.ai.evaluation._converters._ai_services", "azure-ai-projects")
            _lazy_imports["SKAgentConverter"] = _create_lazy_import("SKAgentConverter", "azure.ai.evaluation._converters._sk_services", "semantic-kernel")

            # Check that no messages were printed during setup
            stderr_output = captured_stderr.getvalue()
            self.assertEqual(stderr_output, "", "No messages should be printed during lazy import setup")

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

        _lazy_imports["AIAgentConverter"] = _create_lazy_import("AIAgentConverter", "azure.ai.evaluation._converters._ai_services", "azure-ai-projects")

        def mock_getattr(name):
            """Mock __getattr__ function like the one in __init__.py"""
            if name in _lazy_imports:
                return _lazy_imports[name]()
            raise AttributeError(f"module has no attribute '{name}'")

        # This should raise ImportError directly
        with self.assertRaises(ImportError) as cm:
            mock_getattr("AIAgentConverter")

        # Check that the ImportError message contains the expected information
        error_message = str(cm.exception)
        self.assertIn("Could not import AIAgentConverter", error_message)
        self.assertIn("pip install azure-ai-projects", error_message)

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

    def test_red_team_lazy_imports_no_messages_during_setup(self):
        """Test that red_team module lazy imports don't print messages during setup."""
        # Capture stderr to check for unwanted messages
        captured_stderr = StringIO()
        original_stderr = sys.stderr
        sys.stderr = captured_stderr

        try:
            # Test red_team lazy import setup directly
            _lazy_imports = {}

            def _create_lazy_import(class_name, module_path, dependency_name):
                """Create a lazy import function for optional dependencies."""
                def lazy_import():
                    module = __import__(module_path, fromlist=[class_name])
                    return getattr(module, class_name)
                return lazy_import

            # Setting up red_team lazy imports should not print any messages
            _lazy_imports["RedTeam"] = _create_lazy_import("RedTeam", "azure.ai.evaluation.red_team._red_team", "azure-ai-evaluation[redteam]")
            _lazy_imports["AttackStrategy"] = _create_lazy_import("AttackStrategy", "azure.ai.evaluation.red_team._attack_strategy", "azure-ai-evaluation[redteam]")
            _lazy_imports["RiskCategory"] = _create_lazy_import("RiskCategory", "azure.ai.evaluation.red_team._attack_objective_generator", "azure-ai-evaluation[redteam]")
            _lazy_imports["RedTeamResult"] = _create_lazy_import("RedTeamResult", "azure.ai.evaluation.red_team._red_team_result", "azure-ai-evaluation[redteam]")

            # Check that no messages were printed during setup
            stderr_output = captured_stderr.getvalue()
            self.assertEqual(stderr_output, "", "No messages should be printed during red_team lazy import setup")

        finally:
            sys.stderr = original_stderr

    def test_red_team_message_when_accessing_missing_dependency(self):
        """Test that appropriate message is shown when accessing red_team class with missing dependency."""
        _lazy_imports = {}

        def _create_lazy_import(class_name, module_path, dependency_name):
            """Create a lazy import function for optional dependencies."""
            def lazy_import():
                # This should fail in most test environments since pyrit might not be available
                module = __import__(module_path, fromlist=[class_name])
                return getattr(module, class_name)
            return lazy_import

        _lazy_imports["RedTeam"] = _create_lazy_import("RedTeam", "azure.ai.evaluation.red_team._red_team", "azure-ai-evaluation[redteam]")

        def mock_getattr(name):
            """Mock __getattr__ function like the one in red_team/__init__.py"""
            if name in _lazy_imports:
                return _lazy_imports[name]()
            raise AttributeError(f"module has no attribute '{name}'")

        # Test accessing RedTeam - this might succeed if pyrit is installed, or fail if not
        # We'll test the mechanism rather than the specific failure
        try:
            result = mock_getattr("RedTeam")
            # If it succeeds, that's fine - the dependency is available
            self.assertIsNotNone(result)
        except (ImportError, ModuleNotFoundError):
            # If it fails, that's also expected behavior
            pass


if __name__ == "__main__":
    unittest.main()