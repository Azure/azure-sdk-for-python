# Overview

This document provides an introduction to the msrest model and dpg model architectures.

## msrest Model

The Azure Python Management SDK, generated from Swagger specifications using [@autorest/python](https://www.npmjs.com/package/@autorest/python), implements the msrest model pattern for SDK consumers. The following example illustrates the fundamental structure of an msrest model:

```python
from typing import Optional
from azure.mgmt.example._utils import serialization as _serialization

class Person(_serialization.Model):
    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "parent_name": {"key": "parentName", "type": "str"},
    }

    def __init__(self, *, name: Optional[str] = None, parent_name: Optional[str] = None) -> None:
        ...
```

Usage example:

```python
msrest_model = Person(name="xxx", parent_name="xxx")
print(msrest_model.name)
print(msrest_model.parent_name)

# Access model as a dictionary
json_model = msrest_model.as_dict()
print(json_model["name"])
print(json_model["parentName"])
```

## dpg Model

The Azure Python Management SDK, generated from [typespec](https://github.com/microsoft/typespec/) using [@azure-tools/typespec-python](https://www.npmjs.com/package/@azure-tools/typespec-python), implements the dpg model pattern. The following example demonstrates the fundamental structure of a dpg model:

```python
from typing import Optional, Any, Mapping, overload
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

Usage example:

```python
dpg_model = Person(name="xxx", parent_name="xxx")
print(dpg_model.name)
print(dpg_model.parent_name)

# Access model directly as a dictionary
print(dpg_model["name"])
print(dpg_model["parentName"])
```

## Summary

The dpg model maintains full compatibility with the msrest model while offering enhanced usability features.
