# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from .._utils import serialization as _serialization


def _attach_msrest_compat(cls: type) -> type:
    """Class decorator that grafts old msrest ``Model`` methods onto a class
    that defines ``_attribute_map`` (and optionally ``_validation``).

    Use this for public models that are *not* subclasses of the generated
    TypeSpec model (and therefore don't get ``_ModelBackCompatMixin`` via
    inheritance).
    """
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
        "__eq__",
        "__ne__",
        "__str__",
    ):
        if _name in vars(_serialization.Model):
            setattr(cls, _name, vars(_serialization.Model)[_name])
    return cls


__all__: List[str] = []


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
