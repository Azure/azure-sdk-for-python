"""
Pytest configuration and shared fixtures for unit tests.
"""

# Workaround: importing agent_framework (via mcp) can fail with
# KeyError: 'pydantic.root_model' unless this module is imported first.
import pydantic.root_model  # noqa: F401

import site
import sys
from pathlib import Path


# Ensure we don't import user-site packages that can conflict with the active
# environment (e.g., a user-installed cryptography wheel causing PyO3 errors).
try:
	user_site = site.getusersitepackages()
	if user_site:
		sys.path[:] = [p for p in sys.path if p != user_site]
except Exception:
	# Best-effort: if site isn't fully configured, proceed without filtering.
	pass

# Ensure package sources are importable during tests
tests_root = Path(__file__).resolve()
src_root = tests_root.parents[4]
packages_root = tests_root.parents[2] / "packages"

for path in (packages_root, src_root):
	if str(path) not in sys.path:
		sys.path.insert(0, str(path))
