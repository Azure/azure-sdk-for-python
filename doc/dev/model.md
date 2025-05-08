# Overview

This doc introduces msrest model and dpg model.

## msrest model

Azure Python Mgmt SDK that is generated from swagger with tool [@autorest/python](https://www.npmjs.com/package/@autorest/python) provides msrest model for SDK users. Here is the rough structure of msrest model:

```python
from azure.mgmt.example._utils.serialization as _serialization

class Person(_serialization.Model):
    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "parent_name": {"key": "parentName", "type": "str"},
    }

    def __init__(self, *, name: Optional[str] = None, parent_name: Optional[str] = None) -> None:
        ...
```
Here is the usage example:

```python
msrest_model = Person(name="xxx", parent_name="xxx")
print(msrest_model.name)
print(msrest_model.parent_name)

# use model as dict
json_model = msrest_model.as_dict()
print(json_model["name"])
print(json_model["parentName"])
```

## dpg model

Azure Python Mgmt SDK that is generated from [typespec](https://github.com/microsoft/typespec/) with tool [@azure-tools/typespec-python](https://www.npmjs.com/package/@azure-tools/typespec-python) provides msrest model for SDK users. Here is rough structure of dpg model:

```python
from azure.mgmt.example._utils.model_base import Model as _Model, rest_field

class Person(_Model):
    name: Optional[str] = rest_field()
    parent_name: Optional[str] = rest_field(name="parentName")

    @overload
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        parent_name: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
```

Here is usage example:

```python
dpg_model = Person(name="xxx", parent_name="xxx")
print(dpg_model.name)
print(dpg_model.parent_name)

# use model as dict directly
print(dpg_model["name"])
print(dpg_model["parentName"])
```

## Summary

We can see dpg model is not only compatible with msrest model, but also more convenient to use.
