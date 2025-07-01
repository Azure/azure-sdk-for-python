# SDK AI Guide - Getting Started

An AI agent to simplfy the workflows in the azure-sdk-for-python repo.

## Prerequisites

1. **Repository setup**: Open the azure-sdk-for-python repository at the root directory in VS Code
2. **MCP servers**: Ensure the azure-sdk-python-mcp server and azure-sdk-mcp server are running and connected in VS Code
3. **Package manager**: Install `uv` package manager (`pip install uv` or follow [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/))
4. **GitHub CLI authentication**: Run `gh auth login`
5. **Feature branch**: Create a new branch with `git checkout -b <branch-name>`


## Where to Start

**The best starting point is understanding what you need to accomplish for your specific package:**

### 📋 Quick Start Prompts

- `"What needs to be done to release azure-ai-projects?"`
- `"I need to update azure-eventgrid"`
- `"Check package release readiness for [package-name]"`
- `"Generate a Python SDK using TypeSpec"`
- `"Help me update [package-name] - walk me through the workflow"`

**Copilot will ask clarifying questions to understand your specific scenario and guide you through the exact steps needed.**


## Common Workflows

### 1. New Package Generation

For creating a completely new SDK from TypeSpec:

- `"Generate a Python SDK using TypeSpec"`
- `"Start TypeSpec SDK generation for Python"`
- `"Generate SDK from tspconfig.yaml at <path>"`

### 2. Package Updates & Fixes

For existing packages that need updates or fixes:

- `"What validation issues does azure-ai-projects have?"`
- `"Fix the pylint warnings in my package"`
- `"Update my package to the latest TypeSpec version"`

### 3. Release Preparation

For packages ready for release:

- `"Prepare azure-ai-projects for release"`
- `"Check if my package is ready to release"`
- `"Update documentation and changelog for release"`

### 2. Follow Copilot's Workflow

Copilot will automatically:

1. **Assess your package** - Check current health status and identify blockers
2. **Verify environment** - Check dependencies and virtual environment
3. **Generate SDK** - Run TypeSpec generation (~5-6 minutes)
4. **Validate code** - Run Pylint, MyPy, Pyright, Verifytypes, Sphinx, Mindependency, Bandit, Black, Samples, Breaking changes (~3-5 minutes each)
5. **Update docs** - Create/update CHANGELOG.md and version files
6. **Commit changes** - Add, commit, and push to your branch
7. **Create PR** - Generate pull request in draft mode
8. **Handoff** - Provide PR link for azure-rest-api-specs agent

## Package Health & Release Readiness

**Start here to understand what your package needs:**

### Health Status Check
```
What is the health status of azure-ai-projects?
```

This reports the library's status from [aka.ms/azsdk/python/health](https://www.aka.ms/azsdk/python/health) and identifies:
- Release blocking issues
- Validation failures that need fixing
- Missing documentation or tests
- Recommended next steps

### Release Readiness Check
```
Check package release readiness for azure-ai-projects
```

This comprehensive check includes:
- Pipeline status verification
- APIView review status
- Changelog validation
- Namespace approval status
- All release-blocking requirements

### 3. Your Actions

- Provide file paths when requested
- Review and approve code changes
- Confirm commit messages
- Review PR title and description

## Expected Timeline

- **Total time**: 10-15 minutes
- **SDK Generation**: 5-6 minutes
- **Validation**: 3-5 minutes per step
- **Documentation**: 2-4 minutes

## Next Steps

After PR creation, if working through the release plan steps with the DevEx agent, use the **azure-rest-api-specs agent** with your PR link to complete the release process.
