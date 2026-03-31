---
mode: "agent"
description: "Bump version for all agentserver packages"
tools: ["editFiles"]
---

# Bump Agentserver Package Versions

Given a new version string and changelog message, update all three agentserver packages:

1. Update `VERSION` in all three `_version.py` files to the new version:
   - `azure-ai-agentserver-core/azure/ai/agentserver/core/_version.py`
   - `azure-ai-agentserver-agentframework/azure/ai/agentserver/agentframework/_version.py`
   - `azure-ai-agentserver-langgraph/azure/ai/agentserver/langgraph/_version.py`

2. Update the `azure-ai-agentserver-core==<old_version>` dependency pin in:
   - `azure-ai-agentserver-agentframework/pyproject.toml`
   - `azure-ai-agentserver-langgraph/pyproject.toml`

3. Add a new changelog entry at the TOP of each package's `CHANGELOG.md` (right after `# Release History`) with today's date in `YYYY-MM-DD` format. Use the appropriate section headers (`### Features Added`, `### Bugs Fixed`, `### Other Changes`).

4. If additional external dependency version changes are specified, update those in the relevant `pyproject.toml` files.

## User provides
- **New version** (e.g. `1.0.0b17`)
- **Changelog message** (e.g. "Upgraded dependencies.")
- **Any external dependency changes** (optional)
