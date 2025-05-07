# Overview

This doc introduces msrest model and dpg model.

## msrest model

Azure Python Mgmt SDK that is generated from swagger with tool autorest.python provides msrest model for SDK users. Here is the structure of msrest model:

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

json_model = msrest_model.as_dict()
print(json_model["name"])
print(json_model["parentName"])

```

## dpg model

Azure Python Mgmt SDK that is generated from typespec with tool @azure-tools/typespec-python provides msrest model for SDK users. Here is the structure of dpg model:

Here is usage example:



## Summary

We can see dpg model is not only compatible with msrest model, but also more convenient to use.

