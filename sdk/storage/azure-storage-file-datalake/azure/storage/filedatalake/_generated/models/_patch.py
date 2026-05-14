# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any

from .._utils.model_base import Model as _Model, _MyMutableMapping

__all__: list[str] = []


# ---------------------------------------------------------------------------
# Backcompat shim for legacy ``knack.util.todict`` consumers (e.g. Azure CLI).
# knack checks ``hasattr(obj, '_asdict')`` (namedtuple convention) BEFORE
# falling back to ``obj.__dict__``.  TypeSpec ``_Model`` instances stash all
# fields in ``__dict__['_data']`` so a naive ``__dict__`` walk sees nothing.
# Returning the model contents with REST wire-name keys at every level
# matches what msrest models exposed when knack walked their ``__dict__``
# and camelCased the snake_case attributes -- preserving the JSON shape the
# Azure CLI's ``_transformers.py`` expects.
# ---------------------------------------------------------------------------


def _asdict_value(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, _MyMutableMapping):
        return _patched_namedtuple_asdict(v)
    if isinstance(v, dict):
        return {k: _asdict_value(val) for k, val in v.items()}
    if isinstance(v, (list, tuple, set)):
        return type(v)(_asdict_value(x) for x in v)
    return v


def _patched_namedtuple_asdict(self) -> dict:
    """Mirror msrest behaviour: include every declared field (REST wire
    name) even when the value was never set, so legacy CLI consumers
    that subscript by key (e.g. ``result['start']``) don't raise
    ``KeyError`` for omitted optional fields."""
    result: dict = {}
    rest_fields = getattr(type(self), "_attr_to_rest_field", None) or {}
    data = getattr(self, "_data", {}) or {}
    for rf in rest_fields.values():
        result[rf._rest_name] = _asdict_value(data.get(rf._rest_name))
    for k, v in data.items():
        if k not in result:
            result[k] = _asdict_value(v)
    return result


_Model._asdict = _patched_namedtuple_asdict


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
