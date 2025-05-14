# Overview

Our new generation of SDK incorporates several refinements to enhance efficiency and clarity. Although we have made considerable efforts to maintain backward compatibility, certain specific behaviors have been modified. This document outlines how you can update your source code to accommodate these changes. If you encounter an issue not addressed in this document, please submit a report on GitHub.

## Access to the model as a dictionary

### Access for Old SDK

```python
from azure.mgmt.test.models import Model
model = Model(name="xxx")
print(model.name)

# access property as dictionary
json_model = model.as_dict()
print(json_model["name"])
```

### Access for New SDK

```python
from azure.mgmt.test.models import Model
model = Model(name="xxx")
print(model.name)

print(model["name"]) # access property as dictionary directly, no need to call `as_dict()` anymore
print(model.as_dict()["name"]) # still support `as_dict()`
```

You can access properties of the SDK model as before. When accessing properties as a dictionary, you no longer need to call `.as_dict()`, which provides greater convenience. This also means that editing the model using dictionary syntax directly modifies the model. The `as_dict()` method continues to provide an independent copy of the model's dictionary representation in memory.

### `as_dict()` Note

The positional parameter `keep_readonly` with default value `True` in the old SDK's `as_dict()` method has been renamed to a keyword-only parameter `exclude_readonly` with default value `False` in the new SDK.

## Model hierarchy

Previous SDK models attempted to implement a flat hierarchy that did not accurately reflect the underlying REST API structure, which occasionally led to complications. Beginning with this new generation of SDK, the attribute hierarchy in models will directly mirror the REST API layer. Nevertheless, to ensure backward compatibility, the new SDK model continues to support a simplified flat hierarchy. In instances where the hierarchy was previously flattened across multiple levels, code adjustments will be necessary:

```python
# Old SDK model
model = Model(...)
print(model.properties_name) # A
print(model.properties_properties_name) # B

# New SDK model
model_after_migration = Model(...)
print(model_after_migration.properties_name) # A
print(model_after_migration.properties.name) # equivalent to A
print(model_after_migration.properties_properties_name) # Will now raise an AttributeError
print(model_after_migration.properties.properties.name) # recommended approach after migration
```

## Additional properties

### Old SDK model

To support [additional properties](https://www.apimatic.io/openapi/additionalproperties), SDK models included an `additional_properties` parameter:

```python
model = Model(additional_properties={"hello": "world"})
print(model.additional_properties) # output is `{"hello": "world"}`
print(model.as_dict()) # output is `{"hello": "world"}`
```

### New SDK model for additional properties

Now, SDK models inherently support additional properties through dictionary-like behavior. The `additional_properties` parameter is no longer supported in new SDK models, and they can no longer be read using `.additional_properties`.

```python
model = Model(additional_properties={"hello": "world"}) # no longer supported
model = Model({"hello": "world"})
# or
model = Model()
model.update({"hello": "world"})
# or 
model = Model()
model["hello"] = "world"

print(model) # output is `{"hello": "world"}`
```

## `__str__` for SDK model

### `__str__` for Old SDK Model

```python
model = Model(type_name="type")
print(str(model)) # output is `{"type_name": "type"}`
```

### `__str__` for New SDK Model

```python
model = Model(type_name="type")
print(str(model)) # output is `{"typeName": "type"}`
```

In the REST API layer, property names use camelCase format, whereas Python SDK typically utilizes snake_case. In the previous SDK version, the string output was presented in snake_case format. The new SDK version, however, outputs strings in camelCase format, maintaining consistency with the REST API layer.
