# Overview

When switching from Swagger to Typespec for SDK generation, there will be some differences in the generated SDK. This document will guide existing SDK users on how to migrate. In the following document, we refer to the former as the Swagger SDK and the latter as the Typespec SDK.

## Model usage

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

# access property as dictionary directly
print(model["name"])
```

Users can access properties of the Typespec SDK model as before. When accessing properties as a dictionary, there is no need to call `.as_dict()` as before, which is more convenient.

### Usage Note

To maintain backward compatibility, Typespec SDK models continue to support the `as_dict` method.

## Model Flattening

Some Swagger SDK models support flattening, which allows users to access nested properties directly. In the Typespec SDK model, this flattening functionality is no longer fully supported. However, for backward compatibility, the Typespec SDK model continues to support simple flattening. For deeply nested flattened properties, code modifications will be necessary:

```python
# swagger SDK model
model1 = Model(...)
print(model1.properties_name) # A
print(model1.properties.name) # equivalent to A
print(model1.properties_properties_name) # B
print(model1.properties.properties.name) # equivalent to B

# Typespec SDK model
model_after_migration = Model(...)
print(model_after_migration.properties_name) # A
print(model_after_migration.properties.name) # equivalent to A
print(model_after_migration.properties_properties_name) # no longer supported
print(model_after_migration.properties.properties.name) # recommended approach after migration
```

## Additional properties

### Swagger SDK model for additional properties

To support [additional properties](https://www.apimatic.io/openapi/additionalproperties), Swagger SDK models include an `additional_properties` parameter:

```python
model = Model(additional_properties={"hello": "world"})
print(model) # output is `{"hello": "world"}`
```

### Typespec SDK model for additional properties

Typespec SDK models inherently support additional properties through dictionary-like behavior. The `additional_properties` parameter is no longer supported in Typespec SDK models, so code modifications will be required for existing SDK users:

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