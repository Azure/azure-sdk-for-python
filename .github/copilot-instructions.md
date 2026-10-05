# AZURE SDK FOR PYTHON - COPILOT INSTRUCTIONS

> **Note**: For general AI agent guidelines and repository overview, see [AGENTS.md](https://github.com/Azure/azure-sdk-for-python/blob/main/AGENTS.md) at the repository root.

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
- [Tool usage guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/tool_usage_guide.md)

**COMMAND:**
```bash
azpysdk pylint .
```

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
- [Tool usage guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/tool_usage_guide.md)
- [MyPy fixing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)

**REQUIREMENTS:**
- Use Python 3.10 compatible environment
- Follow official fixing guidelines
- Run `azpysdk mypy .` from the package directory

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
For all TypeSpec-based SDK workflows (generation, building, validation, testing, versioning, and release), follow #file:skills/azsdk-common-generate-sdk-locally/SKILL.md

### DEFAULT BEHAVIORS
- **Repository:** Use the current workspace as the local SDK repository unless the user specifies a different path.
- **Configuration:** Identify `tsp-location.yaml` from files open in the editor. If unclear, ask the user.

### PYTHON-SPECIFIC RULES
- **Skip build step:** Python packages do not require compilation. After generation, proceed directly to validation and tests.

### REQUIRED CONFIRMATIONS
Ask the user for clarification if repository path or configuration file is ambiguous.

---

## Generated SDK Patches and Customizations

Before adding or changing handwritten patches or customizations of generated Python SDK code (including `_patch.py`), investigate whether the behavior comes from the service spec/configuration or the emitter/generator rather than an intentional SDK customization. Follow the [patch diagnosis checklist](../doc/dev/customize_code/how-to-patch-sdk-code.md#before-adding-or-changing-a-patch) before applying a package-local workaround, including through customization tools. Document the diagnosis and evidence or any investigation blockers; do not claim a generator bug was ruled out without evidence.

---

## MGMT SDK Code Review Rules

### SCOPE
These rules apply to management-plane SDK packages located at `sdk/*/azure-mgmt-*/`.

### REVIEW EXCLUSIONS
- **Skip** the `generated_samples/` and `generated_tests/` folders entirely — do not review generated sample or test code.
- **Skip** source code under `azure/mgmt/**/` **except** `_client.py` — only review `_client.py` among the generated source files.

### VERSION CONSISTENCY
- The version string in `_version.py` **must** match the latest version listed in `CHANGELOG.md`.
- Use the `apiVersions` service-to-version map in `sdk/<service>/azure-mgmt-<package>/_metadata.json` for API-version checks, not the nullable singular `apiVersion`. Missing or malformed maps are unverified evidence, not a reason to fall back to `apiVersion`.
- Preview API versions must use preview SDK versions: if **any value** in `apiVersions` contains `preview` (case-insensitive), the generated package version file (`sdk/<service>/azure-mgmt-<package>/azure/mgmt/<package>/_version.py`) **must** define a beta version such as `1.0.0b1`, not a stable version such as `1.0.0`. This includes maps containing both stable and preview API versions.

### CHANGELOG DATE
- If the release date of the latest version in `CHANGELOG.md` is **more than 3 weeks in the future** from the current date, remind the author to verify and update the date.

### PYPROJECT.TOML STABILITY FLAGS
- **Stable version** (version string does **not** contain `b`):
  - `is_stable` in `pyproject.toml` must be `true`
  - `classifiers` must include `"Development Status :: 5 - Production/Stable"`
- **Preview version** (version string contains `b`):
  - `is_stable` in `pyproject.toml` must be `false`
  - `classifiers` must include `"Development Status :: 4 - Beta"`

### CLIENT SIGNATURE
- The `__init__` method of the client class in `_client.py` must include the parameters `credential`, `subscription_id`, and `base_url` **in that order**. Default values are not checked.
- If `subscription_id` is **not** present in the client's `__init__` signature, `pyproject.toml` must contain `no_sub = true`. If it does not, hint the user to add `no_sub = true` in `pyproject.toml` and regenerate the SDK.

### CLIENT NAME CONSISTENCY
- The client class name in `_client.py`, the client name referenced in `README.md`, and the `title` value in `pyproject.toml` must all be the same.

### INITIAL-RELEASE CLIENT NAME
- For a **confirmed first release** of a management SDK, the synchronous and asynchronous client class names must end with the exact suffix `MgmtClient`.
- A noncompliant name is a **Blocking** finding. Ask the author to add or update the client-name customization in `client.tsp` to choose a descriptive name ending in `MgmtClient`, then regenerate the SDK.
- Do not apply this rename requirement to existing releases, or infer a first release from a missing baseline alone. If first-release status or client declarations cannot be verified, report the check as unverified.

### README CODE SNIPPETS
- Code snippets in `README.md` must follow the real client class signatures and usage patterns. Verify that sample code matches the actual client API.

---

## SDK release

For detailed workflow instructions, see [SDK Release](skills/azsdk-common-sdk-release/SKILL.md).
