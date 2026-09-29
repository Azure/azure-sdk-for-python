---
applyTo: "sdk/**/setup.py,sdk/**/pyproject.toml,sdk/**/setup.cfg,sdk/**/requirements*.txt"
description: "Review Python SDK package metadata and dependency changes for compatibility and correctness."
---

# SDK Dependency Review

Use [the repository packaging guide](../../../doc/dev/packaging.md) and
neighboring packages of the same type as context.

- Check that runtime imports are backed by runtime requirements, test-only
  dependencies are not inadvertently made runtime requirements, and removed
  requirements are not still used.
- Check dependency constraints against the package's supported Python
  versions and the APIs actually used. Identify a concrete incompatibility
  before flagging a version range.
- Check version and stability metadata against the package changelog and
  source version when changed. For management SDKs, the specific
  `pyproject.toml` stability and classifier rules in
  `management.instructions.md` take precedence.
