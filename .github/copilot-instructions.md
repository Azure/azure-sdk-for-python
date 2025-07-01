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
**BEFORE any commands:**
1. Get path to azure-sdk-for-python repo root, and path to tox.ini file
2. Use `verify_setup` tool from azure-sdk-python-mcp server
3. Ensure Python virtual environment is active
4. Install required dependencies if missing using mcp tool `install_packages`

**Virtual Environment Setup:**
```bash
# Create new environment
python -m venv <env_name>

# Activate environment
# Linux/macOS:
source <env_name>/bin/activate
# Windows:
<env_name>\Scripts\activate
```

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

## CODEBASE ARCHITECTURE & PATTERNS

### PACKAGE STRUCTURE

**SDK Organization:**
- `/sdk/{service}/{package-name}/` - Each Azure service lives in its own directory
- `setup.py` - Standard Python packaging with version extraction from `_version.py`
- `tsp-location.yaml` - Links to TypeSpec definitions in azure-rest-api-specs (for TypeSpec-generated SDKs)
- `azure/{namespace}/{module}/` - Actual Python code follows azure.namespace.module pattern
- `tests/` - Tests with recording infrastructure using test proxy
- `samples/` - Working code examples for documentation

**Core Dependencies:**
- `azure-core` - Shared client infrastructure, HTTP pipeline, authentication, error handling
- `azure-identity` - Authentication providers (DefaultAzureCredential, etc.)
- Generated models inherit from `azure.core._serialization.Model`

### CODE GENERATION PATTERNS

**TypeSpec-Generated Packages:**
- Use `tsp-location.yaml` to specify Azure REST API specs commit hash
- Generated files in `azure/{namespace}/{service}/models/` and `azure/{namespace}/{service}/operations/`
- Client classes follow pattern: `{Service}Client` with credential and endpoint parameters
- All HTTP operations are auto-generated with proper typing and documentation

**Manual/Hybrid Packages:**
- Client libraries may extend generated code with higher-level convenience methods
- Follow Azure SDK Design Guidelines for method signatures and error handling

### TESTING INFRASTRUCTURE

**Test Proxy System:**
- Tests inherit from `AzureRecordedTestCase` in `devtools_testutils`
- Use `@recorded_by_proxy` decorator for functional tests that make HTTP calls
- Environment variables loaded via `EnvironmentVariableLoader` with fake values for recordings
- Recordings stored in separate `azure-sdk-assets` repository, referenced by `assets.json`

**Validation Pipeline:**
- Tox environments: pylint, mypy, pyright, verifytypes, sphinx, samples, bandit, black
- Each must pass for release - failing mypy/pylint/sphinx/tests-ci blocks release
- Use `eng/tox/tox.ini` with `--root .` flag for all validation commands

### NAMESPACE MANAGEMENT

**Python Packaging:**
- Namespace packages allow `azure.service.feature` imports across separate PyPI packages
- `find_packages(exclude=["azure", "azure.service"])` prevents namespace package conflicts
- `_version.py` pattern for version management: `VERSION = "1.0.0"`

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
