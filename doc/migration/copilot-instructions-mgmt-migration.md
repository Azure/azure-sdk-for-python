# Azure SDK Python Migration Instructions for LLMs

**File: AzureSdkPythonMigration.instructions.md**

## Purpose

These instructions help LLMs automatically upgrade Azure SDK Python management libraries from AutoRest-generated versions to TypeSpec-generated versions with minimal user intervention.

## Summary of Breaking Changes

The TypeSpec migration introduces three major categories of breaking changes:

### 1. Operation Design Changes
- **Query/Header Parameters**: Now require keyword-only arguments (never positional)
- **Conditional Operations**: `if_match`/`if_none_match` replaced with `etag` + `match_condition` enum
- **Parameter Ordering**: Only path and body parameters remain positional

### 2. Hybrid Model Changes
- **Dictionary Access**: Direct dict operations, camelCase keys, renamed `as_dict()` parameters
- **Property Flattening**: Multi-level flattened properties removed, use nested access
- **Additional Properties**: No more `additional_properties` parameter, use dict syntax
- **Serialization**: `.serialize()` and `.deserialize()` methods removed
- **String Representation**: Output now in camelCase to match REST API

### 3. Authentication Changes
- **Credential Libraries**: Migration from `azure.common.credentials` to `azure.identity`
- **Credential Parameter**: Now keyword-only in client constructors

## Trigger

When a user says: **"azsdk upgrade \<package-name\> \<version\>"**

Example: `azsdk upgrade azure-mgmt-compute 30.0.0`

## Migration TODO List

**IMPORTANT: Use the `manage_todo_list` tool throughout this migration to track progress and ensure no steps are missed.**

When starting the migration, create a TODO list with these items:

1. **Pre-migration assessment** - Detect Python environment and run initial tests
2. **Package upgrade** - Update dependencies and install with uv
3. **Post-upgrade test** - Run tests/linting to identify breaking changes
4. **Fix parameter signatures** - Update positional vs keyword-only parameters
5. **Fix hybrid model usage** - Update model access patterns (dictionary, hierarchy, serialization)
6. **Fix LRO patterns** - Add begin_ prefixes and handle pollers
7. **Fix authentication** - Update credential imports and usage
8. **Final validation** - Run tests to ensure all issues resolved
9. **Summary and documentation** - Report changes to user

Mark each todo as `in-progress` when starting work on it, and `completed` when finished. This helps track migration progress and ensures systematic completion.

## Step-by-Step Migration Process

### Phase 1: Pre-Migration Assessment

**Use `manage_todo_list` to mark "Pre-migration assessment" as in-progress**

1. **Check for uv or install it** for faster package management:

   ```bash
   # Check if uv is installed
   uv --version
   
   # If not installed, install it
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or
   pip install uv
   ```

2. **Identify the Python package configuration**:
   - `pyproject.toml` → Modern format, use with uv
   - `requirements.txt` → Consider migrating to pyproject.toml with uv
   - `setup.py` or `setup.cfg` → Legacy, migrate to pyproject.toml
   - `Pipfile` → Replace with pyproject.toml and uv

3. **Determine test command** by checking for:
   - `pytest` in dependencies → Use `uv run pytest`
   - `unittest` in test files → Use `uv run python -m unittest`
   - `tox.ini` → Use `uv run tox`
   - Default to `uv run pytest` if tests exist

4. **Run initial tests** to establish baseline:

   ```bash
   # Using uv for consistent environment
   uv run pytest                    # for pytest
   uv run python -m unittest        # for unittest
   uv run python -m pytest tests/   # common pattern
   ```

   - If tests fail, note the errors but continue (existing issues)
   - If linting is configured: `uv run mypy` or `uv run flake8`

**Mark "Pre-migration assessment" as completed and "Package upgrade" as in-progress**

### Phase 2: Package Upgrade

**If not using pyproject.toml, migrate first:**

```bash
# Quick migration to pyproject.toml with uv
uv init --name azure-project --python 3.9

# Add existing dependencies
# From requirements.txt:
uv add $(cat requirements.txt | grep -v '^#' | tr '\n' ' ')

# From setup.py (extract manually or use):
uv add azure-mgmt-xxx azure-identity  # Add your packages
```

4. **Update package version** in pyproject.toml:

   ```toml
   # pyproject.toml
   [project]
   dependencies = [
       "azure-mgmt-compute>=30.0.0,<31.0.0",  # Updated version
       "azure-identity>=1.15.0",
       "azure-core>=1.30.0",  # Required for hybrid models
   ]
   ```

5. **Install dependencies** with uv:

   ```bash
   # Fast installation with uv
   uv sync
   
   # Or if adding new package
   uv add azure-mgmt-compute@">=30.0.0"
   ```

6. **Run post-upgrade tests** to identify breaking changes:

   ```bash
   # Use uv run for consistent environment
   uv run pytest
   ```

   - Capture all errors, especially:
     - TypeError (parameter signature issues)
     - AttributeError (model property access issues)
     - KeyError (dictionary access issues)
     - ImportError (authentication changes)

**Mark "Package upgrade" as completed and start marking specific fix categories as in-progress**

### Phase 3: Fix Breaking Changes

Apply fixes based on TypeSpec migration patterns for Python:

#### 3.1 Parameter Signature Fixes

**Mark "Fix parameter signatures" as in-progress when working on these**

**Pattern Detection:** Look for TypeErrors about positional arguments:
- `TypeError: xxx() takes n positional arguments but m were given`
- `TypeError: xxx() got multiple values for argument`
- `TypeError: xxx() got an unexpected keyword argument 'if_match'`
- Methods with many positional arguments (>3)

**Fixes to Apply:**

##### 3.1.1 Basic Parameter Migration

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
```

##### 3.1.2 Query and Header Parameters

**Query/header parameters MUST be keyword-only:**

```python
# OLD: Query parameters as positional
environments = client.organization_operations.list_environments(
    "resource_group",
    "org_name", 
    10,        # page_size as positional
    "token"    # page_token as positional
)

# NEW: Query parameters as keyword-only
environments = client.organization_operations.list_environments(
    "resource_group",     # Path param - positional
    "org_name",          # Path param - positional
    page_size=10,        # Query param - keyword-only
    page_token="token"   # Query param - keyword-only
)
```

##### 3.1.3 Conditional Operation Parameters

**Conditional headers have been redesigned:**

```python
# OLD: Using if_match/if_none_match
from azure.mgmt.containerservicefleet import ContainerServiceFleetManagementClient

fleet = client.fleets.begin_create_or_update(
    resource_group_name="rg",
    fleet_name="fleet1",
    resource=fleet_data,
    if_match="W/\"etag-value\""  # Old conditional header
)

# NEW: Using etag + match_condition enum
from azure.mgmt.containerservicefleet import ContainerServiceFleetManagementClient
from azure.core import MatchConditions

fleet = client.fleets.begin_create_or_update(
    resource_group_name="rg",     # Path param
    fleet_name="fleet1",          # Path param
    resource=fleet_data,          # Body param
    etag="W/\"etag-value\"",     # Keyword-only
    match_condition=MatchConditions.IfNotModified  # Keyword-only
)
```

**Conditional Parameter Migration Map:**

| Old Pattern | New Pattern |
|------------|-------------|
| `if_match="<etag>"` | `etag="<etag>", match_condition=MatchConditions.IfNotModified` |
| `if_none_match="<etag>"` | `etag="<etag>", match_condition=MatchConditions.IfModified` |
| `if_match="*"` | `match_condition=MatchConditions.IfPresent` |
| `if_none_match="*"` | `match_condition=MatchConditions.IfMissing` |

**Rules for Parameter Migration:**
- **Path parameters** (in URL path): Remain positional
- **Body parameters** (request body): Remain positional (usually as dict)
- **Query parameters** (in URL query string): **ALWAYS** keyword-only
- **Header parameters** (HTTP headers): **ALWAYS** keyword-only
- **Conditional parameters** (if_match/if_none_match): Replace with etag + match_condition
- **Optional parameters**: Become keyword-only

**Common Parameter Patterns:**

```python
# List operations - query params become keyword-only
# OLD
resources = client.resources.list(
    filter_expr,  # Positional query param
    expand,       # Positional query param
    top,          # Positional query param
    skip          # Positional query param
)

# NEW
resources = client.resources.list(
    filter=filter_expr,  # Keyword-only
    expand=expand,       # Keyword-only
    top=top,            # Keyword-only
    skip=skip           # Keyword-only
)

# Operations with mixed parameters
# OLD
result = client.resources.create_or_update(
    resource_group,      # Path
    name,               # Path
    api_version,        # Query
    if_match,           # Header
    resource_data       # Body
)

# NEW
result = client.resources.create_or_update(
    resource_group,                    # Path - positional
    name,                             # Path - positional
    resource_data,                    # Body - positional
    api_version=api_version,          # Query - keyword-only
    etag=if_match,                    # Header - keyword-only
    match_condition=MatchConditions.IfNotModified  # Header - keyword-only
)
```

#### 3.2 Hybrid Model Usage Fixes

**Mark "Fix hybrid model usage" as in-progress when working on these**

Hybrid models have a dual dictionary and model nature with several breaking changes:

##### 3.2.1 Dictionary Access Pattern Changes

**Pattern Detection:** Look for:
- `.as_dict()` method calls with `keep_readonly` parameter
- Code expecting `snake_case` keys in dictionary output
- Direct dictionary operations on models

**Fixes:**

```python
# OLD: Using as_dict() with keep_readonly
model = Model(my_name="example")
json_model = model.as_dict(keep_readonly=True)
print(json_model["my_name"])  # snake_case key

# NEW: Direct dictionary access (PREFERRED)
model = Model(my_name="example")
print(model["myName"])  # Direct access, camelCase key

# NEW: If as_dict() still needed
json_model = model.as_dict(exclude_readonly=False)  # Parameter renamed
print(json_model["myName"])  # Returns camelCase

# BACKCOMPAT: If you need snake_case keys
from azure.core.serialization import as_attribute_dict
json_model = as_attribute_dict(model, exclude_readonly=False)
print(json_model["my_name"])  # Preserves snake_case
```

**Migration Rules:**
- Replace `keep_readonly=True` → `exclude_readonly=False`
- Replace `keep_readonly=False` → `exclude_readonly=True`
- Update `snake_case` keys → `camelCase` keys
- Prefer direct dictionary access: `model["key"]` over `model.as_dict()["key"]`

##### 3.2.2 Model Hierarchy (Flattened Properties)

**Pattern Detection:** Look for:
- Properties with multiple underscores (e.g., `properties_properties_name`)
- AttributeError on nested property access
- KeyError when accessing flattened properties

**Fixes:**

```python
# OLD: Artificially flattened properties
model.properties_name                    # Single-level flattening
model.properties_properties_name         # Multi-level flattening
json_model["properties_properties_name"] # Flattened in dict

# NEW: Actual REST API hierarchy
model.properties_name                    # Still works (backcompat for single-level)
model.properties.name                    # PREFERRED: mirrors API structure
model.properties.properties.name         # Multi-level: use actual nesting
model["properties"]["properties"]["name"] # Dictionary access

# BACKCOMPAT: For complex flattened access
from azure.core.serialization import as_attribute_dict
model_dict = as_attribute_dict(model)
print(model_dict["properties_properties_name"])  # Works with flattened
```

**Migration Rules:**
- Single underscore properties: May still work but prefer nested access
- Multiple underscore properties: Must use nested dot notation
- Replace `obj.level1_level2_prop` → `obj.level1.level2.prop`
- For dict access: `obj["level1_level2_prop"]` → `obj["level1"]["level2"]["prop"]`

##### 3.2.3 Additional Properties Handling

**Pattern Detection:** Look for:
- `TypeError` with `additional_properties` parameter
- Access to `.additional_properties` attribute
- Setting custom properties on models

**Fixes:**

```python
# OLD: Using additional_properties parameter
model = Model(additional_properties={"custom": "value"})
print(model.additional_properties)

# NEW: Direct dictionary syntax
# Option 1: Pass in constructor
model = Model({"custom": "value"})

# Option 2: Use update
model = Model()
model.update({"custom": "value"})

# Option 3: Direct assignment
model = Model()
model["custom"] = "value"

# Access is direct
print(model["custom"])  # No .additional_properties needed
```

##### 3.2.4 Serialization/Deserialization Changes

**Pattern Detection:** Look for:
- `.serialize()` method calls
- `.deserialize()` static method calls
- Custom serialization workflows

**Fixes:**

```python
# OLD: Explicit serialize/deserialize methods
import json

# Serialization
model = Model(name="example")
serialized = model.serialize()
json_string = json.dumps(serialized)

# Deserialization
data = json.loads(json_string)
model = Model.deserialize(data)

# NEW: Models are inherently serializable
import json

# Serialization (multiple options)
model = Model(name="example")
json_string = json.dumps(model.as_dict())  # Explicit
# or
json_string = json.dumps(dict(model))      # Convert to dict

# Deserialization - direct constructor
data = json.loads(json_string)
model = Model(data)  # Constructor handles it

# BACKCOMPAT: For exact old serialize() format
from azure.core.serialization import as_attribute_dict
serialized = as_attribute_dict(model, exclude_readonly=False)
```

**Migration Rules:**
- `model.serialize()` → `model.as_dict()` or `dict(model)`
- `Model.deserialize(data)` → `Model(data)`
- `serialize(keep_readonly=True)` → `as_dict(exclude_readonly=False)`
- `serialize(keep_readonly=False)` → `as_dict(exclude_readonly=True)`

##### 3.2.5 String Representation Changes

**Pattern Detection:** Look for:
- Test assertions comparing model string output
- Code parsing model string representations
- Logging that expects specific format

**Fixes:**

```python
# OLD: String output in snake_case
model = Model(type_name="example")
print(model)  # {"type_name": "example"}

# NEW: String output in camelCase (matches REST API)
model = Model(type_name="example")
print(model)  # {"typeName": "example"}

# If you need snake_case for compatibility
from azure.core.serialization import as_attribute_dict
print(as_attribute_dict(model))  # {"type_name": "example"}
```

##### 3.2.6 Model Instantiation Patterns

**Pattern Detection:** Look for:
- Complex nested model construction
- Models with many parameters
- TypeError about unexpected keyword arguments

**Fixes:**

```python
# OLD: Deep nesting with model classes
from azure.mgmt.compute.models import (
    VirtualMachine, StorageProfile, OSDisk, ImageReference
)

vm = VirtualMachine(
    location="eastus",
    hardware_profile=HardwareProfile(
        vm_size="Standard_D2s_v3"
    ),
    storage_profile=StorageProfile(
        os_disk=OSDisk(
            create_option="FromImage",
            managed_disk=ManagedDisk(
                storage_account_type="Premium_LRS"
            )
        ),
        image_reference=ImageReference(
            publisher="Canonical",
            offer="UbuntuServer",
            sku="18.04-LTS",
            version="latest"
        )
    )
)

# NEW: Prefer dictionary for nested structures
vm = {
    "location": "eastus",
    "properties": {
        "hardwareProfile": {
            "vmSize": "Standard_D2s_v3"
        },
        "storageProfile": {
            "osDisk": {
                "createOption": "FromImage",
                "managedDisk": {
                    "storageAccountType": "Premium_LRS"
                }
            },
            "imageReference": {
                "publisher": "Canonical",
                "offer": "UbuntuServer",
                "sku": "18.04-LTS",
                "version": "latest"
            }
        }
    }
}

# Can still use top-level model if needed
from azure.mgmt.compute.models import VirtualMachine
vm = VirtualMachine(vm)  # Pass dict to constructor
```

**Quick Reference - Model Migration Priority:**
1. Fix dictionary access (`.as_dict()` parameters, key casing)
2. Fix property flattening (multi-level underscore properties)
3. Remove `additional_properties` usage
4. Update serialization/deserialization
5. Handle string representation changes
6. Simplify nested model construction with dictionaries

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
   # Run tests with uv
   uv run pytest
   
   # Run type checking if available
   uv run mypy .
   
   # Run linting if configured
   uv run pylint src/
   uv run flake8
   ```

8. **Verify success:**
   - All tests should pass
   - No import errors
   - No TypeErrors or AttributeErrors
   - Type checking passes (if using mypy)
   - Model access patterns work correctly

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

**`TypeError: xxx() got an unexpected keyword argument 'if_match'`**
→ Replace with `etag` and `match_condition` parameters (see conditional operations section)

**`TypeError: xxx() got an unexpected keyword argument 'if_none_match'`**
→ Replace with `etag` and `match_condition` parameters

**`TypeError: __init__() got an unexpected keyword argument 'additional_properties'`**
→ Remove `additional_properties` parameter, use direct dict syntax instead

**`AttributeError: 'dict' object has no attribute 'xxx'`**
→ Use dictionary access: `obj['xxx']` instead of `obj.xxx`

**`AttributeError: 'Model' object has no attribute 'properties_properties_xxx'`**
→ Multi-level flattening removed, use `obj.properties.properties.xxx`

**`AttributeError: 'Model' object has no attribute 'additional_properties'`**
→ Access additional properties directly: `model["custom_key"]`

**`AttributeError: 'Model' object has no attribute 'serialize'`**
→ Use `model.as_dict()` or `dict(model)` instead

**`AttributeError: type object 'Model' has no attribute 'deserialize'`**
→ Use `Model(data)` constructor instead of `Model.deserialize(data)`

**`KeyError: 'my_property'`**
→ Keys are now camelCase: use `'myProperty'` instead of `'my_property'`

**`KeyError: 'properties_nested_value'`**
→ Flattened keys don't work in dict access: use `obj["properties"]["nested"]["value"]`

**`ImportError: cannot import name 'ServicePrincipalCredentials'`**
→ Replace with azure-identity credential classes

**`NameError: name 'MatchConditions' is not defined`**
→ Import from azure.core: `from azure.core import MatchConditions`

### Type Checking Errors (mypy)

**`Argument n to "xxx" has incompatible type`**
→ Update to use dictionary or correct model type

**`Unexpected keyword argument`**
→ Parameter might now be part of body dict or renamed

**`Missing positional argument`**
→ Some parameters now keyword-only

**`error: "dict[str, Any]" has no attribute "xxx"`**
→ Model is being used as dict, either use `model.xxx` for attribute or `model["xxx"]` for dict

### Model-Specific Error Patterns

**Error when calling `.as_dict(keep_readonly=True)`**
```python
# Fix: Parameter renamed
model.as_dict(exclude_readonly=False)
```

**Error accessing nested properties with underscores**
```python
# OLD: model.properties_vm_size
# NEW: model.properties.vm_size
```

**Error with model string comparison in tests**
```python
# OLD: assert str(model) == '{"my_field": "value"}'
# NEW: assert str(model) == '{"myField": "value"}'
```

**Error with additional properties**
```python
# OLD: Model(name="test", additional_properties={"custom": "value"})
# NEW: Model(name="test", custom="value") or Model({"name": "test", "custom": "value"})
```

**Error with conditional operations**
```python
# OLD: client.update(name, data, if_match="etag-123")
# NEW: 
from azure.core import MatchConditions
client.update(name, data, etag="etag-123", match_condition=MatchConditions.IfNotModified)
```

**Error with query parameters as positional**
```python
# OLD: client.list("rg", "name", 10, "token")  # TypeError
# NEW: client.list("rg", "name", page_size=10, page_token="token")
```

## Python Environment Commands Reference

```bash
# uv (recommended - 10-100x faster than pip)
uv init --name project --python 3.9
uv add azure-mgmt-xxx@">=version"
uv sync
uv run pytest
uv run python script.py
uv pip list
uv pip show azure-mgmt-xxx

# Quick migration from requirements.txt
uv init
uv add $(cat requirements.txt | grep -v '^#' | tr '\n' ' ')

# Testing with uv
uv run pytest
uv run python -m unittest discover
uv run mypy src/
uv run black . --check
uv run ruff check

# Type checking
uv run mypy src/
uv run pyright

# Linting
uv run pylint src/
uv run flake8
uv run black . --check
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
- **Parameter rules are critical:** 
  - Path and body params: positional
  - Query and header params: ALWAYS keyword-only
  - Conditional params: Replace with etag + match_condition
- **Hybrid model patterns:** Apply all 6 model migration patterns systematically:
  1. Dictionary access changes (`.as_dict()` parameters, camelCase keys)
  2. Property flattening fixes (nested dot notation for multi-level)
  3. Additional properties (remove parameter, use dict syntax)
  4. Serialization updates (no `.serialize()/.deserialize()` methods)
  5. String representation (expect camelCase in output)
  6. Model instantiation (prefer dicts for nested structures)
- **Operation patterns:** Fix conditional operations systematically:
  - Import `MatchConditions` from `azure.core`
  - Replace `if_match` → `etag` + `MatchConditions.IfNotModified`
  - Replace `if_none_match` → `etag` + `MatchConditions.IfModified`
- **Use uv for speed:** Always prefer uv over pip/poetry for 10-100x faster operations
- **Prefer dictionaries:** TypeSpec SDKs work well with dict representations
- **Check imports carefully:** Many imports change between versions
- **Test incrementally:** Run tests after each major change category
- **Preserve existing patterns:** Don't change unrelated code
- **Add type hints:** When updating function signatures, preserve/add type hints
- **Handle None values:** Use `.get()` or check for None before accessing nested properties
- **Be precise with errors:** Match error messages exactly to apply correct fixes
- **Use backcompat helpers:** When needed, use `azure.core.serialization` utilities:
  - `as_attribute_dict()` for snake_case compatibility
  - `is_generated_model()` to detect SDK models
  - `attribute_list()` to get model attributes
- **Document breaking changes:** Keep notes on what changed for the summary

## Common Migration Patterns Reference

### Quick Reference: Parameter Classification

To determine if a parameter should be positional or keyword-only:

1. **Path parameters** (part of the URL path like `/resource-groups/{resourceGroupName}`): **POSITIONAL**
2. **Body parameters** (request payload): **POSITIONAL** (as single dict/object)
3. **Query parameters** (URL query string like `?api-version=2024-01-01`): **ALWAYS KEYWORD-ONLY**
4. **Header parameters** (HTTP headers like `If-Match`): **ALWAYS KEYWORD-ONLY**
5. **Conditional parameters** (`if_match`/`if_none_match`): **REPLACED** (see below)
6. **Optional parameters**: **KEYWORD-ONLY**

### Quick Reference: Conditional Operations

| Old Pattern | New Pattern |
|------------|-------------|
| `if_match="<etag>"` | `etag="<etag>", match_condition=MatchConditions.IfNotModified` |
| `if_none_match="<etag>"` | `etag="<etag>", match_condition=MatchConditions.IfModified` |
| `if_match="*"` | `match_condition=MatchConditions.IfPresent` |
| `if_none_match="*"` | `match_condition=MatchConditions.IfMissing` |

Always import: `from azure.core import MatchConditions`

### Quick Reference: Hybrid Model Migration

| Old Pattern | New Pattern | Backcompat Option |
|------------|-------------|-------------------|
| `model.as_dict(keep_readonly=True)` | `model.as_dict(exclude_readonly=False)` | `as_attribute_dict(model, exclude_readonly=False)` |
| `json["my_property"]` | `json["myProperty"]` | Use `as_attribute_dict()` for snake_case |
| `model.properties_nested_prop` | `model.properties.nested.prop` | `as_attribute_dict(model)["properties_nested_prop"]` |
| `Model(additional_properties={...})` | `Model({...})` or `model.update({...})` | N/A |
| `model.serialize()` | `model.as_dict()` or `dict(model)` | `as_attribute_dict(model)` |
| `Model.deserialize(data)` | `Model(data)` | N/A |
| `str(model)` returns snake_case | `str(model)` returns camelCase | `str(as_attribute_dict(model))` |

### Quick Fix Patterns

```python
# If you see: client.method(a, b, c, d, e)
# And get: TypeError about too many positional arguments
# Check parameter types and fix:
# - If a, b are path params and c is body: client.method(a, b, c, d=d, e=e)
# - If a, b are path params and rest are query: client.method(a, b, c=c, d=d, e=e)
# - If a, b are path and c,d,e should be in body: client.method(a, b, {"c": c, "d": d, "e": e})

# If you see: resource.some_nested_property
# And get: AttributeError
# Try: resource.some.nested.property

# If you see: if_match="etag-value"
# Replace with: etag="etag-value", match_condition=MatchConditions.IfNotModified

# If you see: if_none_match="*"
# Replace with: match_condition=MatchConditions.IfMissing

# If you see: model.as_dict(keep_readonly=True)
# Replace with: model.as_dict(exclude_readonly=False)

# If you see: from azure.common.credentials import X
# Replace with: from azure.identity import Y

# If you see: Model.deserialize(json_data)
# Replace with: Model(json_data)

# If you need snake_case for compatibility:
from azure.core.serialization import as_attribute_dict
snake_case_dict = as_attribute_dict(model)

# If you need conditional operations:
from azure.core import MatchConditions
result = client.update(name, data, etag=etag, match_condition=MatchConditions.IfNotModified)
```

This migration should be **fully automated** with minimal user intervention beyond the initial command.