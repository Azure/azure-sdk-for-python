# Azure SDK Python Mgmt Migration Instructions for LLMs

**File: AzureSdkPythonMgmtMigration.instructions.md**

## Purpose

These instructions help LLMs automatically upgrade Azure SDK Python management libraries from AutoRest-generated versions to TypeSpec-generated versions with minimal user intervention.

## Trigger

When a user says: **"azsdk upgrade \<package-name\> \<version\>"**

Example: `azsdk upgrade azure-mgmt-compute 30.0.0`

## Migration TODO List

**IMPORTANT: Use the `manage_todo_list` tool throughout this migration to track progress and ensure no steps are missed.**

When starting the migration, create a TODO list with these items:

1. **Pre-migration assessment** - Detect Python environment and run initial tests
2. **Package upgrade** - Update requirements/setup.py and install dependencies
3. **Post-upgrade test** - Run tests/linting to identify breaking changes
4. **Fix parameter signatures** - Update positional vs keyword-only parameters
5. **Fix hybrid model usage** - Update model instantiation patterns
6. **Fix LRO patterns** - Add begin\_ prefixes and handle pollers
7. **Fix authentication** - Update credential imports and usage
8. **Final validation** - Run tests to ensure all issues resolved
9. **Summary and documentation** - Report changes to user

Mark each todo as `in-progress` when starting work on it, and `completed` when finished. This helps track migration progress and ensures systematic completion.

## Step-by-Step Migration Process

### Phase 1: Pre-Migration Assessment

**Use `manage_todo_list` to mark "Pre-migration assessment" as in-progress**

1. **Identify the Python environment** by checking for these files in order:

   - `pyproject.toml` with Poetry → Use `poetry` commands
   - `pyproject.toml` without Poetry → Use `uv` commands (if `uv` exists) else system `pip`
   - `Pipfile` → Use `pipenv` commands
   - `requirements.txt` → Use `uv pip` with requirements file if `uv` exists, else system `pip`
   - `setup.py` or `setup.cfg` → Use `uv pip install -e .` if `uv` exists, else system `pip install -e .`
   - Default to `uv pip` if none found and `uv` exists, else use system `pip`

2. **Determine test command** by checking for:

   - `tox.ini` → Use `tox` for testing
   - `pytest.ini` or `pytest` in dependencies → Use `pytest`
   - `unittest` in test files → Use `python -m unittest`
   - Check `setup.py` or `pyproject.toml` for test commands

3. **Run initial tests** to establish baseline:

   ```bash
   # Use the appropriate command based on environment detected
   pytest                    # for pytest
   python -m unittest        # for unittest
   tox                      # for tox
   python -m pytest tests/   # common pattern
   ```

   - If tests fail, note the errors but continue (existing issues)
   - If linting is configured, run: `pylint` or `flake8` or `mypy`

**Mark "Pre-migration assessment" as completed and "Package upgrade" as in-progress**

### Phase 2: Package Upgrade

4. **Update package version** in appropriate file:

   For `requirements.txt`:

   ```txt
   # OLD
   azure-mgmt-compute==29.1.0

   # NEW
   azure-mgmt-compute==30.0.0
   ```

   For `setup.py`:

   ```python
   install_requires=[
       "azure-mgmt-compute>=30.0.0,<31.0.0",
   ]
   ```

   For `pyproject.toml`:

   ```toml
   [tool.poetry.dependencies]
   azure-mgmt-compute = "^30.0.0"
   ```

5. **Install dependencies** using detected package manager:

   ```bash
   pip install -r requirements.txt     # for requirements.txt
   pip install -e .                     # for setup.py
   poetry install                       # for Poetry
   pipenv install                       # for Pipenv
   ```

6. **Run post-upgrade tests** to identify breaking changes:

   ```bash
   # Use same test command as step 3
   pytest
   ```

   - Capture all errors, especially TypeError and AttributeError
   - Note import errors and missing modules

**Mark "Package upgrade" as completed and start marking specific fix categories as in-progress**

### Phase 3: Fix Breaking Changes

Apply fixes based on TypeSpec migration patterns for Python:

#### 3.1 Parameter Signature Fixes

**Mark "Fix parameter signatures" as in-progress when working on these**

**Pattern Detection:** Look for TypeErrors about positional arguments:

- `TypeError: xxx() takes n positional arguments but m were given`
- `TypeError: xxx() got multiple values for argument`
- Methods with many positional arguments (>3)

**Fixes to Apply:**

```python
# OLD: AutoRest-generated (all parameters could be positional)
client.resource_groups.create_or_update(
    resource_group_name,
    location,
    tags,
    managed_by,
    properties
)

# NEW: TypeSpec-generated (only path and body params are positional)
client.resource_groups.create_or_update(
    resource_group_name,  # Path param - stays positional
    {                     # Body param - stays positional
        "location": location,
        "tags": tags,
        "managed_by": managed_by,
        "properties": properties
    }
)

# Alternative with separate body construction
body = {
    "location": location,
    "tags": tags
}
client.resource_groups.create_or_update(
    resource_group_name,
    body
)
```

**Rules for Parameter Migration:**

- **Path parameters** (in URL path): Remain positional
- **Body parameters** (request body): Remain positional (usually as dict)
- **Query parameters** (in URL query string): Become keyword-only
- **Header parameters** (HTTP headers): Become keyword-only
- **Optional parameters**: Become keyword-only

**Common Parameter Patterns:**

```python
# List operations - all params become keyword-only
# OLD
resources = client.resources.list(filter_expr, expand, top, skip)

# NEW
resources = client.resources.list(
    filter=filter_expr,
    expand=expand,
    top=top,
    skip=skip
)

# Get operations - path params stay positional
# OLD
resource = client.resources.get(resource_group, name, api_version)

# NEW
resource = client.resources.get(
    resource_group,  # Path param
    name,           # Path param
    api_version=api_version  # Query param becomes keyword-only
)
```

#### 3.2 Hybrid Model Usage Fixes

**Mark "Fix hybrid model usage" as in-progress when working on these**

**Pattern Detection:** Look for:

- Direct model instantiation with many parameters
- `AttributeError: 'dict' object has no attribute`
- Model constructor TypeErrors

**Fixes:**

```python
# OLD: Using model classes directly
from azure.mgmt.compute.models import VirtualMachine, StorageProfile

vm = VirtualMachine(
    location="eastus",
    hardware_profile=HardwareProfile(vm_size="Standard_D2s_v3"),
    storage_profile=StorageProfile(...)
)

# NEW: Option 1 - Use dictionaries (preferred for TypeSpec)
vm = {
    "location": "eastus",
    "properties": {
        "hardwareProfile": {"vmSize": "Standard_D2s_v3"},
        "storageProfile": {...}
    }
}

# NEW: Option 2 - Models with keyword arguments
from azure.mgmt.compute.models import VirtualMachine

vm = VirtualMachine(
    location="eastus",
    properties={
        "hardwareProfile": {"vmSize": "Standard_D2s_v3"},
        "storageProfile": {...}
    }
)
```

**Dictionary vs Model Rules:**

- Prefer dictionaries for nested structures
- Use models when type hints are needed
- Mix approaches based on code readability

#### 3.3 Long Running Operations (LRO) Fixes

**Mark "Fix LRO patterns" as in-progress when working on these**

**Pattern Detection:** Look for:

- Methods without `begin_` that should have it
- `AttributeError: 'NoneType' object has no attribute 'result'`
- Timeout errors or hanging operations

**Fixes:**

```python
# OLD: Inconsistent LRO handling
poller = client.virtual_machines.create_or_update(
    resource_group_name,
    vm_name,
    parameters
)
result = poller.result()

# NEW: Consistent begin_ prefix
poller = client.virtual_machines.begin_create_or_update(
    resource_group_name,  # Path param - positional
    vm_name,              # Path param - positional
    parameters            # Body param - positional
)
result = poller.result()

# For methods that already had begin_
# OLD
poller = client.deployments.begin_create_or_update(
    resource_group,
    deployment_name,
    properties,
    mode,
    template,
    parameters
)

# NEW - consolidate into body parameter
poller = client.deployments.begin_create_or_update(
    resource_group,     # Path param
    deployment_name,    # Path param
    {                   # Body param
        "properties": properties,
        "mode": mode,
        "template": template,
        "parameters": parameters
    }
)
```

**LRO Method Patterns:**

- Add `begin_` if missing for: create, update, delete operations
- Keep poller.result() pattern unchanged
- Update parameter signatures per rules above

#### 3.4 Authentication Fixes

**Mark "Fix authentication" as in-progress when working on these**

**Pattern Detection:** Look for:

- `ImportError: cannot import name 'ServicePrincipalCredentials'`
- `azure.common.credentials` imports
- Credential parameter as positional argument

**Fixes:**

```python
# OLD: Using deprecated azure.common
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient

credentials = ServicePrincipalCredentials(
    client_id='client-id',
    secret='secret',
    tenant='tenant'
)

client = ResourceManagementClient(credentials, subscription_id)

# NEW: Using azure-identity
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

# Option 1: Specific credential
credential = ClientSecretCredential(
    tenant_id='tenant',
    client_id='client-id',
    client_secret='secret'
)

# Option 2: Default credential chain
credential = DefaultAzureCredential()

# Note: credential is now keyword-only
client = ResourceManagementClient(
    credential=credential,  # Keyword-only
    subscription_id=subscription_id
)
```

**Credential Migration Map:**

- `ServicePrincipalCredentials` → `ClientSecretCredential`
- `UserPassCredentials` → `UsernamePasswordCredential`
- `MSIAuthentication` → `ManagedIdentityCredential`
- Generic/unknown → `DefaultAzureCredential`

**Mark relevant fix categories as completed when done**

### Phase 4: Additional Pattern Fixes

#### 4.1 Enum Handling

**Pattern Detection:** Enum-related AttributeErrors or string conversion issues

```python
# OLD: Enum member access
from azure.mgmt.compute.models import VirtualMachineSizeTypes
size = VirtualMachineSizeTypes.standard_d2s_v3

# NEW: String literals or new enum pattern
size = "Standard_D2s_v3"  # Direct string usage

# Or if enum still exists
from azure.mgmt.compute.models import VirtualMachineSizeTypes
size = VirtualMachineSizeTypes.STANDARD_D2S_V3  # Note: uppercase
```

#### 4.2 Exception Handling

```python
# OLD: CloudError from azure.common
from azure.common.exceptions import CloudError

try:
    resource = client.resources.get(rg, name)
except CloudError as e:
    print(e.message)

# NEW: azure.core exceptions
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

try:
    resource = client.resources.get(rg, name)
except ResourceNotFoundError as e:
    print(f"Not found: {e}")
except HttpResponseError as e:
    print(f"HTTP error: {e.status_code}")
```

#### 4.3 Pagination Updates

```python
# OLD: Custom pagination handling
resources = client.resources.list()
all_resources = []
for page in resources:
    all_resources.extend(page)

# NEW: Iterator protocol
resources = client.resources.list()
all_resources = list(resources)  # Automatic pagination

# Or iterate directly
for resource in client.resources.list():
    process(resource)
```

### Phase 5: Validation

**Mark "Final validation" as in-progress**

7. **Run final tests** after applying all fixes:

   ```bash
   # Run tests
   pytest

   # Run type checking if available
   mypy .

   # Run linting if configured
   pylint src/
   flake8
   ```

8. **Verify success:**
   - All tests should pass
   - No import errors
   - No TypeErrors or AttributeErrors
   - Type checking passes (if using mypy)

**Mark "Final validation" as completed**

### Phase 6: Completion

**Mark "Summary and documentation" as in-progress**

9. **Report results** to user:
   - List all files modified
   - Summarize types of changes made
   - Note any manual review items
   - Confirm successful upgrade

**Mark "Summary and documentation" as completed**

**All todos should now be completed - verify with `manage_todo_list` tool**

## Error-Specific Fix Patterns

### Python Runtime Errors

**`TypeError: xxx() takes n positional arguments but m were given`**
→ Convert extra positional args to keyword arguments or consolidate into body dict

**`TypeError: xxx() got multiple values for argument 'yyy'`**
→ Parameter is now keyword-only, remove positional usage

**`AttributeError: 'dict' object has no attribute 'xxx'`**
→ Use dictionary access: `obj['xxx']` instead of `obj.xxx`

**`AttributeError: module 'azure.mgmt.xxx' has no attribute 'YyyClient'`**
→ Client class may be renamed or moved, check new imports

**`ImportError: cannot import name 'ServicePrincipalCredentials'`**
→ Replace with azure-identity credential classes

### Type Checking Errors (mypy)

**`Argument n to "xxx" has incompatible type`**
→ Update to use dictionary or correct model type

**`Unexpected keyword argument`**
→ Parameter might now be part of body dict

**`Missing positional argument`**
→ Some parameters now keyword-only

## Python Environment Commands Reference

```bash
# pip
pip install -r requirements.txt
pip install -e .
pip install azure-mgmt-xxx==version

# Poetry
poetry add azure-mgmt-xxx@^version
poetry install
poetry run pytest

# Pipenv
pipenv install azure-mgmt-xxx==version
pipenv install --dev
pipenv run pytest

# Testing
pytest
python -m unittest discover
tox
python -m pytest --cov=src tests/

# Type checking
mypy src/
pyright

# Linting
pylint src/
flake8
black . --check
```

## Safety Guidelines

- Always create backups before modifying files
- Use type hints where possible to catch issues early
- Prefer dictionary representations for complex nested structures
- Add `.get()` with defaults for optional dictionary keys
- Use `**kwargs` preservation when wrapping SDK calls
- Test with both sync and async clients if both are used
- Preserve docstrings and comments

## Success Criteria

✅ Package successfully upgraded to target version  
✅ All dependencies resolved without conflicts  
✅ Code runs without runtime errors  
✅ Tests pass (if present)  
✅ Type checking passes (if configured)  
✅ Existing functionality preserved  
✅ Migration follows TypeSpec Python patterns

## Notes for LLMs

- **Use TODO tracking:** Always use the `manage_todo_list` tool to track migration phases
- **Parameter rules are critical:** Remember only path and body params are positional
- **Prefer dictionaries:** TypeSpec SDKs work well with dict representations
- **Check imports carefully:** Many imports change between versions
- **Test incrementally:** Run tests after each major change category
- **Preserve existing patterns:** Don't change unrelated code
- **Add type hints:** When updating function signatures, preserve/add type hints
- **Handle None values:** Use `.get()` or check for None before accessing nested properties
- **Be precise with errors:** Match error messages exactly to apply correct fixes
- **Document breaking changes:** Keep notes on what changed for the summary

## Common Migration Patterns Reference

### Quick Reference: Parameter Classification

To determine if a parameter should be positional or keyword-only:

1. **Path parameters** (part of the URL path like `/resource-groups/{resourceGroupName}`): **POSITIONAL**
2. **Body parameters** (request payload): **POSITIONAL** (as single dict/object)
3. **Query parameters** (URL query string like `?api-version=2024-01-01`): **KEYWORD-ONLY**
4. **Header parameters** (HTTP headers like `If-Match`): **KEYWORD-ONLY**
5. **Optional parameters**: **KEYWORD-ONLY**

### Quick Fix Patterns

```python
# If you see: client.method(a, b, c, d, e)
# And get: TypeError about too many positional arguments
# Check if a, b are path params and combine rest into body:
client.method(a, b, {"c": c, "d": d, "e": e})

# If you see: resource.some_property
# And get: AttributeError
# Try: resource['some_property'] or resource.get('some_property')

# If you see: from azure.common.credentials import X
# Replace with: from azure.identity import Y
# Use the credential migration map above
```

This migration should be **fully automated** with minimal user intervention beyond the initial command.
