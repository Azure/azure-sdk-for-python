"""
Pytest configuration and shared fixtures for unit tests.
"""

import sys
from pathlib import Path

# Ensure package sources are importable during tests
tests_root = Path(__file__).resolve()
src_root = tests_root.parents[4]
packages_root = tests_root.parents[2] / "packages"

for path in (packages_root, src_root):
	if str(path) not in sys.path:
		sys.path.insert(0, str(path))
