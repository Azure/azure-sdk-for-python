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

from .._utils.model_base import Model as _Model, _MyMutableMapping, _RestField


def _patched_getattr(self, name):
    """Lazily initialize _data for subclasses that skip super().__init__()."""
    if name == "_data":
        object.__setattr__(self, "_data", {})
        return self._data
    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


def _patched_setattr(self, name, value):
    """Route attribute writes through _RestField descriptors even when shadowed."""
    if not name.startswith("_"):
        try:
            rf = type(self)._attr_to_rest_field.get(name)
        except AttributeError:
            pass
        else:
            if rf is not None:
                rf.__set__(self, value)
                return
    object.__setattr__(self, name, value)


def _patched_getattribute(self, name):
    """Route attribute reads through _RestField descriptors even when shadowed."""
    if not name.startswith("_"):
        try:
            rest_fields = type(self)._attr_to_rest_field
        except AttributeError:
            pass
        else:
            rf = rest_fields.get(name)
            if rf is not None:
                return rf.__get__(self, type(self))
    return object.__getattribute__(self, name)


# The original ``Model.__new__`` does ``rf._module = cls.__module__`` which
# lets an external subclass (e.g. from azure-storage-file-datalake) overwrite
# ``_module`` on the *shared* descriptor, corrupting type resolution for
# every class that shares it.  This replacement resolves forward references
# against the module that *defined* the rest_field and uses that class's own
# annotations (not merged subclass annotations) to avoid resolving to a type
# whose ``__init__`` can't handle XML elements.


def _patched_new(cls, *args, **kwargs):
    if f"{cls.__module__}.{cls.__qualname__}" not in cls._calculated:
        # Walk only user-defined classes (base-first), stopping before the
        # framework base.  Each _RestField is configured with the module of
        # the class that defined it so forward references resolve correctly.
        user_classes = []
        for c in cls.__mro__:
            if c is _Model:
                break
            user_classes.append(c)

        attr_to_rest_field: dict[str, _RestField] = {}
        for mro_class in reversed(user_classes):
            annotations = getattr(mro_class, "__annotations__", {})
            for k, v in mro_class.__dict__.items():
                if not k.startswith("_") and isinstance(v, _RestField):
                    attr_to_rest_field[k] = v
                    v._module = mro_class.__module__
                    if not v._type:
                        v._type = v._get_deserialize_callable_from_annotation(annotations.get(k, None))
                    if not v._rest_name_input:
                        v._rest_name_input = k

        cls._attr_to_rest_field = attr_to_rest_field
        cls._backcompat_attr_to_rest_field = {
            _Model._get_backcompat_attribute_name(cls._attr_to_rest_field, attr): rf
            for attr, rf in cls._attr_to_rest_field.items()
        }
        cls._calculated.add(f"{cls.__module__}.{cls.__qualname__}")

    return object.__new__(cls)


_MyMutableMapping.__getattr__ = _patched_getattr
_MyMutableMapping.__setattr__ = _patched_setattr
_MyMutableMapping.__getattribute__ = _patched_getattribute
_Model.__new__ = _patched_new


__all__: List[str] = []


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
