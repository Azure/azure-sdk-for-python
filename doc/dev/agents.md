# Using Copilot Agents to Fix CI Issues

This guide helps you leverage GitHub Copilot to troubleshoot and fix common CI (Continuous Integration) issues that can occur in your pull requests for the Azure SDK for Python repository.

## Table of Contents

- [Overview](#overview)
- [Getting Started with Copilot Agents](#getting-started-with-copilot-agents)
- [Common CI Issues and How to Fix Them](#common-ci-issues-and-how-to-fix-them)
  - [MyPy Failures](#mypy-failures)
  - [Pylint Failures](#pylint-failures)
  - [Sphinx/Docstring Failures](#sphinxdocstring-failures)
  - [Test Failures](#test-failures)
  - [Black Formatting Failures](#black-formatting-failures)
  - [Pyright Failures](#pyright-failures)
  - [Dependency Issues](#dependency-issues)
  - [Change Log Verification](#change-log-verification)
- [Using Copilot Agent Mode](#using-copilot-agent-mode)
- [Available Prompts](#available-prompts)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

GitHub Copilot can help you quickly identify and fix CI failures in your pull requests. The Azure SDK for Python repository has several required CI checks that must pass before merging:

**Release-blocking checks (required):**
- **MyPy** - Static type checking
- **Pylint** - Code linting
- **Sphinx** - Documentation validation
- **Tests - CI** - Recorded test execution

**Recommended checks:**
- **Pyright** - Additional static type checking
- **Black** - Code formatting
- **Tests - Live** - Live test execution
- **Tests - Samples** - Sample code validation

For more details on CI checks, see the [Engineering System Checks documentation](../eng_sys_checks.md).

## Getting Started with Copilot Agents

### Prerequisites

- **GitHub Copilot** subscription (individual or business)
- **VSCode** or **VSCode Insiders** with GitHub Copilot extension
- **PowerShell** (required for Azure MCP tools) - [Installation instructions](https://learn.microsoft.com/powershell/scripting/install/installing-powershell)

### Setup

1. Install GitHub Copilot extension in VSCode
2. Ensure PowerShell is installed and restart your IDE to initialize the MCP server
3. Open your Azure SDK for Python repository workspace
4. Open the Copilot chat panel

## Common CI Issues and How to Fix Them

### MyPy Failures

**What it is:** MyPy performs static type checking on your code to ensure type annotations are correct.

**How to ask Copilot for help:**

```
"My PR is failing MyPy checks. Can you help me fix the type errors?"
```

Or provide specific error messages:

```
"I'm getting this MyPy error: 'error: Incompatible return value type (got "str", expected "int")'. How do I fix it?"
```

**Running MyPy locally:**

```bash
cd sdk/your-service/your-package
tox run -e mypy -c ../../../eng/tox/tox.ini --root .
```

**Common fixes Copilot can help with:**
- Adding missing type annotations
- Fixing incompatible return types
- Resolving `Any` type usage
- Adding `TYPE_CHECKING` imports
- Using proper generic types

**Resources:**
- [Static Type Checking Guide](static_type_checking.md)
- [Type Checking Cheat Sheet](static_type_checking_cheat_sheet.md)
- [Engineering System - MyPy](../eng_sys_checks.md#mypy)

### Pylint Failures

**What it is:** Pylint checks your code against Python style guidelines and Azure SDK-specific rules.

**How to ask Copilot for help:**

```
"My PR has pylint warnings. Can you help me understand and fix them?"
```

**Using the Pylint prompt (Agent Mode):**

1. In Copilot **Agent** mode, click `Add Context` → `prompt`
2. Select `next-pylint.prompt.md`
3. Provide the GitHub issue link containing pylint warnings

**Running Pylint locally:**

```bash
cd sdk/your-service/your-package
tox run -e pylint -c ../../../eng/tox/tox.ini --root .
```

For next version of Pylint:

```bash
tox run -e next-pylint -c ../../../eng/tox/tox.ini --root .
```

**Common fixes Copilot can help with:**
- Fixing naming conventions (snake_case, PascalCase)
- Resolving unused imports
- Fixing line length issues
- Addressing Azure SDK-specific guidelines violations
- Properly disabling specific checks when justified

**Important:** Only fix warnings you're confident about. If unsure, ask Copilot to explain the warning first.

**Resources:**
- [Pylint Checking Guide](pylint_checking.md)
- [Azure Pylint Guidelines](https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md)
- [Engineering System - Pylint](../eng_sys_checks.md#pylint)

### Sphinx/Docstring Failures

**What it is:** Sphinx validates that your documentation and docstrings are properly formatted.

**How to ask Copilot for help:**

```
"My PR is failing Sphinx checks. Can you help me fix the docstring errors?"
```

**Running Sphinx locally:**

```bash
cd sdk/your-service/your-package
tox run -e sphinx -c ../../../eng/tox/tox.ini --root .
```

**Common fixes Copilot can help with:**
- Fixing malformed reStructuredText
- Adding missing parameter descriptions
- Fixing cross-reference links
- Ensuring proper docstring format
- Fixing return type documentation

**Resources:**
- [Docstring Guide](docstring.md)
- [Engineering System - Sphinx](../eng_sys_checks.md#sphinx-and-docstring-checker)

### Test Failures

**What it is:** Tests validate that your code works correctly. Failures indicate broken functionality or issues with test setup.

**How to ask Copilot for help:**

```
"My PR tests are failing with [error message]. Can you help me debug this?"
```

Or for specific test environments:

```
"My 'whl' tox environment is failing. What does this mean and how do I fix it?"
```

**Running tests locally:**

```bash
cd sdk/your-service/your-package

# Run all tests (whl environment)
tox run -e whl -c ../../../eng/tox/tox.ini --root .

# Run sdist tests
tox run -e sdist -c ../../../eng/tox/tox.ini --root .

# Run dependency checks
tox run -e depends -c ../../../eng/tox/tox.ini --root .
```

**Common test issues Copilot can help with:**
- Understanding test failures
- Fixing import errors
- Debugging assertion errors
- Setting up test fixtures
- Understanding mocking issues

**Resources:**
- [Testing Guide](tests.md)
- [Engineering System - PR Validation Checks](../eng_sys_checks.md#pr-validation-checks)

### Black Formatting Failures

**What it is:** Black is an opinionated code formatter that ensures consistent code style.

**How to ask Copilot for help:**

```
"My code is failing Black formatting checks. Can you format it properly?"
```

**Running Black locally:**

```bash
cd sdk/your-service/your-package
tox run -e black -c ../../../eng/tox/tox.ini --root . -- .
```

To auto-format your code:

```bash
tox run -e black -c ../../../eng/tox/tox.ini --root . -- --check .
```

**Note:** Black formatting is usually straightforward - just let it auto-format your code.

**Resources:**
- [Engineering System - Black](../eng_sys_checks.md#black)

### Pyright Failures

**What it is:** Pyright is another static type checker that can catch additional type-related issues.

**How to ask Copilot for help:**

```
"My PR is failing Pyright checks. Can you help me resolve the type errors?"
```

**Running Pyright locally:**

```bash
cd sdk/your-service/your-package
tox run -e pyright -c ../../../eng/tox/tox.ini --root .
```

**Common fixes are similar to MyPy** - see the [MyPy section](#mypy-failures).

**Resources:**
- [Static Type Checking Guide](static_type_checking.md)
- [Engineering System - Pyright](../eng_sys_checks.md#pyright)

### Dependency Issues

**What it is:** Checks that ensure your package dependencies are correctly specified and available.

**How to ask Copilot for help:**

```
"My PR is failing dependency checks. Can you help me understand what's wrong with my setup.py requirements?"
```

**Common fixes Copilot can help with:**
- Fixing version constraints in setup.py
- Adding missing dependencies
- Resolving dependency conflicts
- Understanding dev_requirements.txt vs setup.py

**Resources:**
- [Packaging Guide](packaging.md)

### Change Log Verification

**What it is:** Ensures your CHANGELOG.md is properly formatted for the current version.

**How to ask Copilot for help:**

```
"My PR is failing changelog verification. Can you help me format my CHANGELOG.md correctly?"
```

**Common fixes Copilot can help with:**
- Proper changelog format
- Adding required sections
- Correct version formatting
- Following release guidelines

**Resources:**
- [Change Log Guidelines](https://azure.github.io/azure-sdk/policies_releases.html#changelog-guidance)
- [Engineering System - Change Log](../eng_sys_checks.md#change-log-verification)

## Using Copilot Agent Mode

Copilot Agent Mode provides a more powerful, task-oriented way to interact with Copilot.

### How to Use Agent Mode

1. **Open VSCode Insiders** (Agent mode is currently only available in Insiders)
2. **Open Copilot Chat** panel
3. **Switch to Agent mode** (look for the mode selector)
4. **Add context** by clicking `Add Context` button
5. **Select a prompt** from the dropdown (e.g., `next-pylint.prompt.md`)
6. **Send your request** and follow the agent's instructions

### When to Use Agent Mode

- **Complex, multi-step tasks** - When you need Copilot to perform a series of actions
- **Specialized workflows** - When using predefined prompts for specific tasks
- **Debugging complex CI failures** - When standard chat isn't providing enough help

## Available Prompts

The repository includes specialized prompts located in `.github/prompts/`:

### 1. next-pylint.prompt.md

**Purpose:** Fix pylint warnings for a specific library

**How to use:**
1. Get the GitHub issue link containing pylint warnings
2. Use Agent mode with this prompt
3. Provide the issue link when requested
4. Follow instructions to fix warnings

**Best for:** Addressing next-pylint warnings before they become blocking

### 2. check-package-readiness.prompt.md

**Purpose:** Check if a package is ready for release

**How to use:**
1. Use Agent mode with this prompt
2. Provide package name and language when prompted
3. Review readiness report

**Best for:** Pre-release validation

### Creating Custom Prompts

You can create your own prompts following the existing patterns. See [AI Prompt Workflow](ai/ai_prompt_workflow.md) for details.

## Best Practices

### 1. Start Local, Then Ask

Before asking Copilot:
1. Try running the failing check locally
2. Read the error message carefully
3. Check relevant documentation

This helps you provide better context to Copilot.

### 2. Provide Context

When asking Copilot for help:
- ✅ Include the specific error message
- ✅ Mention which CI check is failing
- ✅ Share relevant code snippets
- ✅ Indicate what you've already tried

### 3. Verify Before Committing

Always verify Copilot's suggestions:
- Run the check locally after applying fixes
- Understand what changed and why
- Don't blindly apply suggestions without understanding

### 4. Iterate

If the first solution doesn't work:
- Provide the new error message to Copilot
- Ask follow-up questions
- Try different approaches

### 5. Use the Right Tool

- **Simple questions:** Use regular Copilot chat
- **Complex workflows:** Use Agent mode with prompts
- **Learning:** Ask Copilot to explain errors before fixing

## Troubleshooting

### "I can't access Agent Mode"

**Solution:** Agent mode is currently only available in VSCode Insiders. Download it from [here](https://code.visualstudio.com/insiders/).

### "Azure MCP tools aren't working"

**Solution:** 
1. Ensure PowerShell is installed ([instructions](https://learn.microsoft.com/powershell/scripting/install/installing-powershell))
2. Restart your IDE to initialize the MCP server
3. Check that Copilot extension is up to date

### "Copilot's fixes aren't working"

**Solutions:**
1. Make sure you're running the same check locally that's failing in CI
2. Ensure you're using the correct Python version (3.8+ compatible)
3. Check that your dev environment is properly set up (see [Dev Setup](dev_setup.md))
4. Verify you've installed dependencies: `pip install -r dev_requirements.txt`

### "CI is still failing after fixes"

**Solutions:**
1. Check the PR build logs for the exact error
2. Run all checks locally before pushing
3. Ensure you committed all changes
4. Ask Copilot to review the new error message

### "I need to skip a specific check"

**Reference:** See [Engineering System - Skipping Checks](../eng_sys_checks.md#skipping-entire-sections-of-builds)

**Note:** Skipping checks should be done sparingly and only when necessary.

## Additional Resources

### Documentation
- [Engineering System Checks](../eng_sys_checks.md) - Complete CI check reference
- [Repository Health Status](../repo_health_status.md) - Understanding health reports
- [Testing Guide](tests.md) - Comprehensive testing documentation
- [Copilot Instructions](../../.github/copilot-instructions.md) - Repository-specific Copilot guidance

### Getting Help
- **Teams:** Post in [Language - Python](https://teams.microsoft.com/l/channel/19%3Ab97d98e6d22c41e0970a1150b484d935%40thread.skype/Language%20-%20Python?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121&tenantId=72f988bf-86f1-41af-91ab-2d7cd011db47) channel
- **GitHub:** Open an issue in the repository
- **Documentation:** Check [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)

## Quick Reference

| CI Check | Local Command | Documentation |
|----------|---------------|---------------|
| MyPy | `tox run -e mypy -c ../../../eng/tox/tox.ini --root .` | [MyPy Guide](static_type_checking.md) |
| Pylint | `tox run -e pylint -c ../../../eng/tox/tox.ini --root .` | [Pylint Guide](pylint_checking.md) |
| Next-Pylint | `tox run -e next-pylint -c ../../../eng/tox/tox.ini --root .` | [Pylint Guide](pylint_checking.md) |
| Sphinx | `tox run -e sphinx -c ../../../eng/tox/tox.ini --root .` | [Docstring Guide](docstring.md) |
| Black | `tox run -e black -c ../../../eng/tox/tox.ini --root . -- .` | [Black](../eng_sys_checks.md#black) |
| Pyright | `tox run -e pyright -c ../../../eng/tox/tox.ini --root .` | [Type Checking](static_type_checking.md) |
| Tests (whl) | `tox run -e whl -c ../../../eng/tox/tox.ini --root .` | [Testing Guide](tests.md) |
| Tests (sdist) | `tox run -e sdist -c ../../../eng/tox/tox.ini --root .` | [Testing Guide](tests.md) |

---

**Remember:** GitHub Copilot is a powerful tool, but you should always understand the changes it suggests before applying them. When in doubt, consult the official documentation or ask for help from the team.
