"""
Tests for the Red Team module including utility modules.
"""

import pytest

try:
    import pyrit
    has_pyrit = True
except ImportError:
    has_pyrit = False
    
# This will automatically apply to all test files in this directory
# This avoids having to add the skipif decorator to each test class
pytest.importorskip("pyrit", reason="redteam extra is not installed")