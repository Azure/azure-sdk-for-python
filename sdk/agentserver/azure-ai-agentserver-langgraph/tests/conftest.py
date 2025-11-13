"""
Pytest configuration and shared fixtures for unit tests.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path so we can import modules under test
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))
