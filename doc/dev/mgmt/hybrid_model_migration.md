# Azure SDK Migration Guide: New Hybrid Model Design Generation Breaking Changes

The direct link to this page can be found at aka.ms/azsdk/python/migrate/hybrid-models

This guide covers the breaking changes you'll encounter when upgrading to our new model design and how to fix them in your code.

Our new hybrid models are named as such because they have a dual dictionary and model nature.

## Summary of Breaking Changes

When migrating to the hybrid model design, expect these breaking changes:

| Change                                                                              | Impact                                                    | Quick Fix                                                                         |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------- | --------------------------------------------------------------------------------- |
| [Dictionary Access](#dictionary-access-syntax)                                      | `as_dict()` parameter renamed, output format changed      | Recommended removal of `as_dict()` and directly access model, or replace `keep_readonly=True` with `exclude_readonly=False`, expect `camelCase` keys |
| [Model Hierarchy](#model-hierarchy-reflects-rest-api-structure)                     | Multi-level flattened properties removed                  | Replace `obj.level1_level2_prop` with `obj.level1.level2.prop`                    |
| [Additional Properties](#additional-properties-handling)                            | `additional_properties` parameter removed                 | Use direct dictionary syntax: `model["key"] = value`                              |
| [String Representation](#string-representation-matches-rest-api)                    | Model key output changed from `snake_case` to `camelCase` | Update any code parsing model strings to expect `camelCase`                       |
| [Serialization/Deserialization](#serialization-and-deserialization-methods-removed) | `serialize` and `deserialize` methods removed     | Use dictionary access for serialization, constructor for deserialization          |
| [Reserved Property Names](#reserved-property-name-conflicts)                      | Conflicting names suffixed with `_property`       | Update code to use `_property` suffix: `model.keys` → `model.keys_property`      |

## Detailed Breaking Changes

### Dictionary Access Syntax

**What changed**: Hybrid models support direct dictionary access and use different parameter names and output formats compared to our old models.

**What will break**:

- Code that relies on parameter `keep_readonly` to `.as_dict()`
- Code that expects `snake_case` keys in dictionary output

**Before**:

```python
from azure.mgmt.test.models import Model
model = Model(my_name="example")

# Dictionary access required as_dict()
json_model = model.as_dict(keep_readonly=True)
print(json_model["my_name"])  # snake_case key
```

**After**:

```python
from azure.mgmt.test.models import Model
model = Model(my_name="example")

# Direct dictionary access now works
print(model["myName"])  # Works directly

# as_dict() parameter changed
json_model = model.as_dict(exclude_readonly=False)  # Parameter renamed
print(json_model["myName"])  # Now returns camelCase key (matches REST API)
```

**Migration steps:**

- (Recommended) If you don't need a memory copy as a dict, simplify code by using direct dictionary access: `model["key"]` instead of `model.as_dict()["key"]`
- Replace `keep_readonly=True` with `exclude_readonly=False`
- Update code expecting `snake_case` keys to use `camelCase` keys (consistent with REST API)

**Backcompat option:**
If you need `snake_case` keys and can't easily update your code:

```python
# Requires azure-core >= 1.35.0
from azure.core.serialization import as_attribute_dict

# Returns snake_case keys like the old models
json_model = as_attribute_dict(model, exclude_readonly=False)
print(json_model["my_name"])  # snake_case key preserved
```

### Model Hierarchy Reflects REST API Structure

**What changed**: Hybrid model generation preserves the actual REST API hierarchy instead of artificially flattening it.

**What will break**:

- We've maintained backcompat for attribute access for single-level flattened properties, but multi-level flattening will no longer be supported.
- No level of flattening will be supported when dealing with the response object from `.as_dict()`.

**Before**:

```python
model = Model(...)
print(model.properties_name)                     # Works
print(model.properties_properties_name)          # Works (artificially flattened)
json_model = model.as_dict()
print(json_model["properties_properties_name"])  # Works (artificially flattened)
```

**After**:

```python
model = Model(...)
print(model.properties_name)                      # Still works (single-level flattening maintained for compatibility)
print(model.properties.name)                      # Equivalent to above, preferred approach
print(model["properties_name"])                   # ❌ Raises KeyError
print(model.properties_properties_name)           # ❌ Raises AttributeError
print(model.properties.properties.name)           # ✅ Mirrors actual API structure
print(model["properties_properties_name"])        # ❌ Raises KeyError
print(model["properties"]["properties"]["name"])  # ✅ Mirrors actual API structure
```

**Migration steps:**

- Identify any properties with multiple underscores that represent nested structures
- Replace them with the actual nested property access using dot notation
- Example: `obj.level1_level2_property` → `obj.level1.level2.property`
- This new structure will match your REST API documentation exactly

**Backcompat option:**
For complex flattened property access where direct migration is difficult:

```python
# Requires azure-core >= 1.35.0
from azure.core.serialization import as_attribute_dict

# Handles flattened properties automatically
model_dict = as_attribute_dict(model)
print(model_dict["properties_properties_name"])  # Works with flattened names
```

### Additional Properties Handling

**What changed**: Hybrid models inherently support additional properties through dictionary-like behavior, eliminating the need for a separate additional_properties parameter.
**What will break**:

- Code that passes `additional_properties` parameter
- Code that reads `.additional_properties` attribute

**Before**:

```python
# Setting additional properties
model = Model(additional_properties={"custom": "value"})
print(model.additional_properties)  # {"custom": "value"}
```

**After**:

```python
# ❌ Raises TypeError
model = Model(additional_properties={"custom": "value"})

# ✅ Use these approaches instead
model = Model({"custom": "value"})
# OR
model = Model()
model.update({"custom": "value"})
# OR
model = Model()
model["custom"] = "value"

print(model)  # Shows the additional properties directly
```

**Migration steps:**

- Remove all `additional_properties=` parameters from model constructors
- Replace with direct dictionary syntax or `.update()` calls
- Replace `.additional_properties` attribute access with direct dictionary access

### String Representation Matches REST API

**What changed**: Hybrid models string output uses `camelCase` (matching the REST API) instead of Python's `snake_case` convention in our old models.
**What will break**:

- Code that parses or matches against model string representations
- Tests that compare string output

**Before**:

```python
model = Model(type_name="example")
print(model)  # {"type_name": "example"}
```

**After**:

```python
model = Model(type_name="example")
print(model)  # {"typeName": "example"} - matches REST API format
```

**Migration steps:**

- Update any code that parses model string representations to expect `camelCase`
- Update test assertions that compare against model string output
- Consider using property access instead of string parsing where possible

### Serialization and Deserialization Methods Removed

**What changed**: Hybrid models no longer include explicit `serialize()` and `deserialize()` methods. Models are now inherently serializable through dictionary access, and deserialization happens automatically through the constructor.

**What will break**:

- Code that calls `model.serialize()` or `Model.deserialize()`
- Custom serialization/deserialization workflows
- Code that depends on the specific format returned by the old serialization methods

**Before**:

```python
from azure.mgmt.test.models import Model
import json

# Serialization
model = Model(name="example", value=42)
serialized_dict = model.serialize()  # Returns dict using the REST API name, compatible with `json.dumps` 
json_string = json.dumps(serialized_dict)

# Deserialization
json_data = json.loads(json_string)
model = Model.deserialize(json_data)  # Static method for deserialization
print(model.name)  # "example"

# Custom serialization with options
serialized_full = model.serialize(keep_readonly=True)
serialized_minimal = model.serialize(keep_readonly=False)
```

**After**:

```python
from azure.mgmt.test.models import Model
import json

# Serialization - model is already in serialized format when accessed as dictionary
model = Model(name="example", value=42)

# Method 1: Explicit as_dict() method (recommended)
json_string = json.dumps(model.as_dict())

# Method 2: Direct dictionary access
serialized_dict = {}
for key in model:
    serialized_dict[key] = model[key]

# Deserialization - pass JSON dict directly to constructor
json_data = json.loads(json_string)
model = Model(json_data)  # Constructor handles deserialization automatically
print(model.name)  # "example"

# Advanced: Constructor also accepts keyword arguments
model = Model(name="example", value=42)  # Still works as before
```

**Migration steps:**

- Replace serialization calls: `model.serialize()` → `model` or `model.as_dict()` or `dict(model)`
- Replace deserialization calls: `Model.deserialize(data) → Model(data)`
- Remove any static method imports
- Update serialization options:
  - `serialize(keep_readonly=True)` → `as_dict(exclude_readonly=False)`
  - `serialize(keep_readonly=False)` → `as_dict(exclude_readonly=True)`
- Test serialization format:
  - Verify the output format matches your expectations
  - Check that `camelCase` keys are handled correctly

**Backcompat option:**
If you need the exact same serialization format as the old `serialize()` method:

```python
# Requires azure-core >= 1.35.0
from azure.core.serialization import as_attribute_dict

# Returns the same format as old serialize() method with snake_case keys
serialized_dict = as_attribute_dict(model, exclude_readonly=False)
# For old serialize(keep_readonly=False) behavior:
serialized_dict = as_attribute_dict(model, exclude_readonly=True)
```

### Reserved Property Name Conflicts

**What changed**: Hybrid models now inherit from Python's built-in `dict`. If a REST API property name collides with a `dict` method name (e.g. `keys`, `values`, `items`, `clear`, `update`, `get`, `pop`, `popitem`, `setdefault`, `copy`), the Python emitter appends `_property` to the generated attribute to avoid masking the dictionary method.

**What will break**:

- Constructor calls that pass reserved names as keyword arguments: `Model(keys=...)` now raises or binds incorrectly.
- Attribute access expecting the property value: `model.keys` now refers to the method; calling it without parentheses will not return the property data.

**Before**:

```python
from azure.mgmt.test.models import Model

model = Model(keys={"a": 1}, values=[1, 2, 3])
print(model.keys)      # Property value (old behavior)
print(model.values)    # Property value (old behavior)
print(model.as_dict()["keys"]) # REST layer value
```

**After**:

```python
from azure.mgmt.test.models import Model

# Reserved property names receive a `_property` suffix
model = Model(keys_property={"a": 1}, values_property=[1, 2, 3])

print(model.keys_property)    # ✅ Property value
print(model.values_property)  # ✅ Property value
print(model["keys"])          # REST layer value

# Unsuffixed names are now dict methods
print(list(model.keys()))     # ✅ Dict method listing all serialized keys in the model
print(list(model.values()))   # ✅ Dict method listing all values
```

**Migration steps:**

1. Search for any usage of reserved names as constructor keywords or attribute accesses.
2. Append `_property` to both initialization and attribute access: `Model(keys=...)` → `Model(keys_property=...)`; `model.keys` → `model.keys_property`.
3. Update tests and documentation references accordingly.
4. If you had dynamic code relying on `getattr(model, name)`, ensure you add a rule to transform reserved names to `name + "_property"` first.

---

## Additional Helper Methods

For edge cases and generic code that works with models, Azure Core (version 1.35.0 or later) provides these utility methods in `azure.core.serialization`:

- **`is_generated_model(obj)`**: Check if an object is an SDK-generated model
- **`attribute_list(model)`**: Get list of model attribute names (excluding additional properties)

These are useful for writing generic code that needs to detect or introspect SDK models. These methods work with both the old and new hybrid models.

---

## Why These Changes?

Our hybrid models prioritize consistency with the underlying REST API:

- **Better API Alignment**: Model hierarchy and property names now match your REST API documentation exactly
- **Improved Developer Experience**: Direct dictionary access eliminates extra method calls
- **Consistency**: `camelCase` output matches what you see in REST API responses
- **Maintainability**: Reduced artificial flattening makes the SDK easier to maintain and understand

If you encounter issues not covered here, please file an issue on [GitHub](https://github.com/microsoft/typespec/issues) with tag `emitter:client:python`.
