# Overview

Our new generation of SDK includes some refactoring for efficiency and clarity. While we made a lot of effort to keep the SDK backward compatible, some specific behaviors have changed. This document presents how you can update your source code. To adapt to those changes. Please submit an issue on GitHub, if your problem is not addressed in this document.

## Access to the model as a dictionnary

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

You can access properties of the SDK model as before. When accessing properties as a dictionary, there is no need to call `.as_dict()` as before, which is more convenient. It also means that editing the model using dictionary syntax change the model directly. `as_dict` still provide you an independent copy of the dict of the model in memory.

### `as_dict()` Note

Positional signature `keep_readonly` with default value `True` of `as_dict` in old SDK is renamed to keyword-only signature `exclude_readonly` with default value `False` in new SDK.

## Model hierarchy

Some SDK models were trying to create a flat hierarchy that didn't match the RestAPI underlying layer, causing problems at times. Starting this new generation of SDK, the model hierarchy of attributes will mirror the RestAPI layer. However, for backward compatibility, the new SDK model continues to support simple flat hierarchy. In some cases when the hierarchy was flat on many levels, code modifications will be necessary:

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

## `__str__`

### `__str__` for Old SDK

```python
model = Model(type_name="type")
print(str(model)) # output is `{"type_name": "type"}`
```

### `__str__` for New SDK

```python
model = Model(type_name="type")
print(str(model)) # output is `{"typeName": "type"}`
```

In Rest API layer, the property name is camel case and Python SDK usually use snake case. In old SDK, the string output is snake case, while in new SDK, the string output is camel case which is same with Rest API layer.
