# Overview

Our new generation of SDK includes some refactoring for efficiency and clarity. While we made a lot of effort to keep the SDK backward compatible, some specific behaviors have changed. This document presents how you can update your source code. To adapt to those changes. Please submit an issue on GitHub, if your problem is not addressed in this document.

## Access to the model as a dictionnary

### Swagger SDK

```python
from azure.mgmt.test.models import Model
model = Model(name="xxx")
print(model.name)

# access property as dictionary
json_model = model.as_dict()
print(json_model["name"])
```

### Typespec SDK

```python
from azure.mgmt.test.models import Model
model = Model(name="xxx")
print(model.name)

# access property as dictionary directly, no need to call `as_dict()` anymore
print(model["name"])
```

You can access properties of the SDK model as before. When accessing properties as a dictionary, there is no need to call `.as_dict()` as before, which is more convenient. It also means that editing the model using dictionary syntax change the model directly. `as_dict` still provide you an independent copy of the dict of the model in memory.

### Usage Note

To maintain backward compatibility, Typespec SDK models continue to support the `as_dict` method.

## Model hierarchy

Some SDK models were trying to create a flat hierarchy that didn't match the RestAPI underlying layer, causing problems at times. Starting this new generation of SDK, the model hierarchy of attributes will mirror the RestAPI layer. However, for backward compatibility, the new SDK model continues to support simple flat hierarchy. In some cases when thee hierarchy was flat on many levels, code modifications will be necessary:

```python
# Old SDK model
model = Model(...)
print(model.properties_name) # A
print(model.properties.name) # equivalent to A
print(model.properties_properties_name) # B
print(model.properties.properties.name) # equivalent to B

# New SDK model
model_after_migration = Model(...)
print(model_after_migration.properties_name) # A
print(model_after_migration.properties.name) # equivalent to A
print(model_after_migration.properties_properties_name) # no longer supported
print(model_after_migration.properties.properties.name) # recommended approach after migration
```

## Additional properties

### Swagger SDK model for additional properties

To support [additional properties](https://www.apimatic.io/openapi/additionalproperties), SDK models included an `additional_properties` parameter:

```python
model = Model(additional_properties={"hello": "world"})
print(model) # output is `{"hello": "world"}`
```

### New SDK model for additional properties

Now, SDK models inherently support additional properties through dictionary-like behavior. The `additional_properties` parameter is no longer supported in Typespec SDK models, and they can no longer be read using `.additional_properties`.

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