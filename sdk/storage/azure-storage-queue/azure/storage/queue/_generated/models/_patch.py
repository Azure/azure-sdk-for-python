# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from .._utils import serialization as _serialization

# These public models inherited (transitively) from the autorest
# msrest model, which exposed ``serialize``, ``deserialize``,
# ``from_dict``, ``as_dict``, ``is_xml_model``, and
# ``enable_additional_properties_sending``. After the migration the generated models
# use a different base class. To preserve the public method surface, the methods
# are grafted onto each public class at module load time via the
# ``@_attach_msrest_compat`` decorator.
def _attach_msrest_compat(cls: type) -> type:
    if not hasattr(cls, "_attribute_map"):
        raise TypeError(f"{cls.__name__} must define _attribute_map to use _attach_msrest_compat")
    if not hasattr(cls, "_validation"):
        cls._validation = {}  # type: ignore[attr-defined]
    cls.additional_properties = None  # type: ignore[attr-defined]
    for _name in (
        "serialize",
        "deserialize",
        "from_dict",
        "as_dict",
        "is_xml_model",
        "enable_additional_properties_sending",
        "_infer_class_models",
        "_create_xml_node",
    ):
        setattr(cls, _name, vars(_serialization.Model)[_name])
    return cls



__all__: List[str] = ["_attach_msrest_compat"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """