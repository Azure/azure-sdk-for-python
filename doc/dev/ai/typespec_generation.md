# TypeSpec SDK Generation - Getting Started

Generate Azure SDK for Python from TypeSpec definitions using GitHub Copilot.

## Prerequisites

1. **GitHub CLI authentication**: Run `gh auth login`
2. **Feature branch**: Create a new branch with `git checkout -b <branch-name>`
3. **Python environment**: Ensure `uv` package manager is installed

## Quick Start

### 1. Initiate Generation

In Copilot **Agent** mode, use one of these prompts:

- `"Generate a Python SDK using TypeSpec"`
- `"Start TypeSpec SDK generation for Python"`
- `"Generate SDK from tspconfig.yaml at <path>"`

### 2. Follow Copilot's Workflow

Copilot will automatically:

1. **Verify environment** - Check dependencies and virtual environment
2. **Generate SDK** - Run TypeSpec generation (~5-6 minutes)
3. **Validate code** - Run Pylint, MyPy, Pyright, Verifytypes (~3-5 minutes each)
4. **Update docs** - Create/update CHANGELOG.md and version files
5. **Commit changes** - Add, commit, and push to your branch
6. **Create PR** - Generate pull request in draft mode
7. **Handoff** - Provide PR link for azure-rest-api-specs agent

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

## Library Health Check

Check a library's release readiness:

```
What is the health status of azure-ai-projects?
```

This reports the library's status from [aka.ms/azsdk/python/health](https://www.aka.ms/azsdk/python/health) and identifies any release blockers.

## Next Steps

After PR creation, use the **azure-rest-api-specs agent** with your PR link to complete the release process.

## Useful Prompts

### Starting SDK Generation

**Basic generation:**
```
"Generate a Python SDK using TypeSpec"
"Start TypeSpec SDK generation workflow"
```

**With local TypeSpec project:**
```
"Generate SDK from my local TypeSpec project at sdk/cognitiveservices/azure-ai-projects"
"I have a tspconfig.yaml at [path], generate the Python SDK"
```

**With remote TypeSpec:**
```
"Generate SDK from TypeSpec at https://github.com/Azure/azure-rest-api-specs/blob/main/specification/ai/Azure.AI.Projects/tspconfig.yaml"
```

### Validation and Fixes

**Fix validation issues:**
```
"Fix the pylint warnings in my generated SDK"
"Help me resolve mypy errors"
"Run all validation steps and fix any issues"
```

**Check specific validations:**
```
"Run only pylint validation"
"Check if my SDK passes pyright validation"
```

### Documentation and Release

**Update documentation:**
```
"Update the CHANGELOG.md for my new SDK"
"Set the correct version in _version.py"
```

**Commit and PR:**
```
"Commit my changes and create a pull request"
"Push my SDK changes to a new branch"
```

### Health and Status

**Check library health:**
```
"What is the health status of azure-ai-projects?"
"Check if azure-cognitiveservices-textanalytics is ready for release"
"Show me the CI status for my library"
```
