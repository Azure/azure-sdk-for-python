# AZURE SDK FOR PYTHON - COPILOT INSTRUCTIONS

---

## CORE PRINCIPLES

### RULE 1: DO NOT REPEAT INSTRUCTIONS
**NEVER repeat instructions when guiding users. Users should follow instructions independently.**

### RULE 2: REFERENCE OFFICIAL DOCUMENTATION
**ALWAYS** reference the [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- Link to specific pages when answering guidelines questions
- Use this as the authoritative source for SDK development guidance

### RULE 3: VERIFY ENVIRONMENT FIRST
**REQUIRED CONDITIONS:**
- To use Azure MCP tool calls, users must have PowerShell installed. Provide [PowerShell installation instructions](https://learn.microsoft.com/powershell/scripting/install/installing-powershell) if not installed, and recommend restarting the IDE to start the MCP server.
- When using Copilot from Visual Studio or VS Code (not applicable when using Coding Agent on Github.com):
  - **Always run** the [`azsdk_verify_setup`](../eng/common/instructions/azsdk-tools/verify-setup.instructions.md) tool first to validate the user's development environment for SDK MCP tools.
  - **Do not proceed** with any other tool execution until this step is complete.
  - **Skip this check only** for queries that do not require tool execution.

---

## PYLINT OPERATIONS

### RUNNING PYLINT

**REFERENCE DOCUMENTATION:**
- [Official pylint guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)
- [Tox formatting guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox)

**COMMAND:**
```bash
tox -e pylint --c <path_to_tox.ini> --root .
```

**DEFAULT PATH:** `azure-sdk-for-python/eng/tox/tox.ini`

### FIXING PYLINT WARNINGS

**REFERENCE SOURCES:**
- [Azure pylint guidelines](https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md)
- [Pylint documentation](https://pylint.readthedocs.io/en/stable/user_guide/checkers/features.html)

**ALLOWED ACTIONS:**
✅ Fix warnings with 100% confidence
✅ Use existing file for all solutions
✅ Reference official guidelines

**FORBIDDEN ACTIONS:**
❌ Fix warnings without complete confidence
❌ Create new files for solutions
❌ Import non-existent modules
❌ Add new dependencies/imports
❌ Make unnecessary large changes
❌ Change code style without reason
❌ Delete code without clear justification

---

## MYPY OPERATIONS

### RUNNING AND FIXING MYPY

**REFERENCE DOCUMENTATION:**
- [Tox guidance](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox)
- [MyPy fixing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)

**REQUIREMENTS:**
- Use Python 3.9 compatible environment
- Follow official fixing guidelines
- Use tox mcp tool for running MyPy

---

## Python SDK Health tool

- Use the azure-sdk-python-mcp mcp tool to lookup a library's health status.
- Always include the date of last update based on the Last Refresh date.
- Explanation of statuses can be found here: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/repo_health_status.md
- Release blocking checks are MyPy, Pylint, Sphinx, and Tests - CI. These checks should all PASS. If not PASS, mention that the library is blocked for release.
- If links are available in the table, make the statuses (e.g. PASS, WARNING, etc) you report linked. Avoid telling the user to check the links in the report themselves.
- Don't share information like SDK Owned

### Example

As of <Last Refresh date>, here is the health status for azure-ai-projects:

Overall Status: ⚠️ NEEDS_ACTION

✅ Passing Checks:

Pyright: PASS
Sphinx: PASS
Type Checked Samples: ENABLED
SLA Questions and Bugs: 0

⚠️ Areas Needing Attention:

Pylint: WARNING
Tests - Live: ❓ UNKNOWN
Tests - Samples: ❌ DISABLED
Customer-reported issues: 🔴 5 open issues

❌ Release blocking

Mypy: FAIL
Tests - CI: FAIL

This library is failing two release blocking checks - Mypy and Tests - CI. The library needs attention primarily due to Pylint warnings, disabled sample tests, and open customer-reported issues.

---

## Local SDK Generation and Package Lifecycle (TypeSpec)

### AUTHORITATIVE REFERENCE
For all TypeSpec-based SDK workflows (generation, building, validation, testing, versioning, and release), follow #file:../eng/common/instructions/azsdk-tools/local-sdk-workflow.instructions.md

### DEFAULT BEHAVIORS
- **Repository:** Use the current workspace as the local SDK repository unless the user specifies a different path.
- **Configuration:** Identify `tsp-location.yaml` from files open in the editor. If unclear, ask the user.

### PYTHON-SPECIFIC RULES
- **Skip build step:** Python packages do not require compilation. After generation, proceed directly to validation and tests.

### REQUIRED CONFIRMATIONS
Ask the user for clarification if repository path or configuration file is ambiguous.

---

## SDK release

For detailed workflow instructions, see [SDK Release](https://github.com/Azure/azure-sdk-for-python/blob/main/eng/common/instructions/copilot/sdk-release.instructions.md).
