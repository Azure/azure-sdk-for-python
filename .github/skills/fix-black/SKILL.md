---
name: fix-black
description: Automatically fix black code formatting issues in any Azure SDK for Python package
---

# Fix Black Formatting Issues Skill

This skill automatically fixes black code formatting issues in any Azure SDK for Python package.

## Instructions

1. Activate virtual environment FIRST
2. Install `eng/tools/azure-sdk-tools[build]`
3. Navigate to the package path
4. Run `azpysdk --isolate black .`
5. Review the changes with `git diff`
6. Commit the changes

## Notes

- The Azure SDK uses `eng/black-pyproject.toml` for repo-wide configuration
