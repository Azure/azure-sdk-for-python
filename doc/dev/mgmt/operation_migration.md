# Azure SDK Migration Guide: New Operation Design Generation Breaking Changes

The direct link to this page can be found at aka.ms/azsdk/python/migrate/operations

This guide covers the breaking changes you'll encounter when upgrading to our new operation design and how to fix them in your code.

## Summary of Breaking Changes

When migrating to the operation design, expect these breaking changes:

| Change                                                                              | Impact                                                    | Quick Fix                                                                         |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------- | --------------------------------------------------------------------------------- |
| [Query/Header Parameters](#queryheader-parameters-requiring-keywords) | Query and header signatures changed from positional to keyword-only | Convert all positional parameters to keyword arguments |
| [Conditional Operation](#conditional-operation-parameters-changed) | header signatures `if_match`/`if_none_match` is replaced by `etag`/`match_condition` | Replace `if_match=<specific etag>` with `etag=<specific etag>, match_condition=MatchConditions.IfNotModified`,<br>Replace `if_none_match=<specific etag>` with `etag=<specific etag>, match_condition=MatchConditions.IfModified` |

## Detailed Breaking Changes

### Query/Header Parameters Requiring Keywords

**What changed**: Query and header parameters in operation methods have been changed from positional to keyword-only.

**What will break**:

- Code that passes positional parameters

**Before**:

```python
from azure.mgmt.confluent import ConfluentManagementClient

client = ConfluentManagementClient(...)

# Pass query parameters positionally
environments = client.organization_operations.list_environments(
    "resource_group",
    "org_name", 
    10,        # Pass page_size as positional
    "token"    # Pass page_token as positional
)
```

**After**:

```python
from azure.mgmt.confluent import ConfluentManagementClient

client = ConfluentManagementClient(...)

# ❌ Raises TypeError
environments = client.organization_operations.list_environments(
    "resource_group",
    "org_name", 
    10,
    "token"
)

# ✅ Use these approaches instead
environments = client.organization_operations.list_environments(
    "resource_group",
    "org_name",
    page_size=10,         # Must be passed with a keyword
    page_token="token"    # Must be passed with a keyword
)
```

**Migration steps:**

- Convert all positional parameters to keyword arguments

### Conditional Operation Parameters Changed

**What changed**: Conditional operation headers `if_match` and `if_none_match` have been replaced with more semantic `etag` and `match_condition` parameters that use enum values to describe match conditions.

**What will break**:

- Code using `if_match` or `if_none_match` parameters

**Before**:

```python
from azure.mgmt.containerservicefleet import ContainerServiceFleetManagementClient

client = ContainerServiceFleetManagementClient(...)

# Update the resource only if the latest etag matches the value provided in this header
fleet = client.fleets.begin_create_or_update(
    resource_group_name="rg",
    fleet_name="fleet1", 
    resource=fleet_operation,
    if_match="<specific etag>"
)
```

**After**:

```python
from azure.mgmt.containerservicefleet import ContainerServiceFleetManagementClient
from azure.core import MatchConditions

client = ContainerServiceFleetManagementClient(...)

# Use enum to describe match condition
fleet = client.fleets.begin_create_or_update(
    resource_group_name="rg",
    fleet_name="fleet1",
    resource=fleet_operation,
    etag="<specific etag>",
    match_condition=MatchConditions.IfNotModified
)
```

**Migration steps:**

- Import `MatchConditions` from `azure.core`
- Replace `if_match="<specific etag>"` with `etag="<specific etag>", match_condition=MatchConditions.IfNotModified`
- Replace `if_none_match="<specific etag>"` with `etag="<specific etag>", match_condition=MatchConditions.IfModified`
- Replace `if_match="*"` with `match_condition=MatchConditions.IfPresent`
- Replace `if_none_match="*"` with `match_condition=MatchConditions.IfMissing`

## Why These Changes?

Our operations prioritize consistency with the underlying REST API:

- **Better API Alignment**: Keyword-only parameters improve traceability between code and request body.
- **Improved Developer Experience**: Keyword-only parameters enable IDEs to provide rich type hints with parameter names.
- **Maintainability**: Enum-based conditions makes the SDK easier to maintain and understand.

If you encounter issues not covered here, please file an issue on [GitHub](https://github.com/microsoft/typespec/issues) with tag `emitter:client:python`.
