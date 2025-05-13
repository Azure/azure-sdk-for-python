# Overview

When switch generation from swagger to typespec, there will be some differences in the generated SDK. This doc will guide existing SDK users how to migrate. In the following doc, we call the former swagger SDK and the latter typespec SDK.

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

We can see users can access properties of typespec SDK model as before. When access property as dictionary, there is no need to calling `.as_dict()` as before which is more convenient.

### Usage Note

To keep backward compatibility, typespec SDK models continue to support method `as_dict`.

## Model Flattening

Some swagger SDK model supports flattening that users could access nested property directly. In typespec SDK model, we don't support flattening anymore. But for backward compatibility, typespec SDK model continue to support simple flattening. However, for deeply nested flattened properties, code updates may be required:

```python
# swagger SDK model
model1 = Model(...)
print(model1.properties_name) # A
print(model1.properties.name) # equivalent to A
print(model1.properties_properties_name) # B
print(model1.properties.properties.name) # equivalent to B

# typespec SDK model
model_after_migration = Model(...)
print(model_after_migration.properties_name) # A
print(model_after_migration.properties.name) # equivalent to A
print(model_after_migration.properties_properties_name) # no longer work
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

Typespec SDK model inherently support additional properties through dictionary-like behavior. And typespec SDK model don't support `additional_properties` so code update may be required for existing SDK users.

```python
model = Model(additional_properties={"hello": "world"}) # no longer works
model = Model({"hello": "world"})
# or
model = Model()
model.update({"hello": "world"})
# or 
model = Model()
model["hello"] = "world"

print(model) # output is `{"hello": "world"}`
```