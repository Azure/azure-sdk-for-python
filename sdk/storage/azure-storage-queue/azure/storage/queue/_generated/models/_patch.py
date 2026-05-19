# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
# TODO: Waiting on Emitter Perf updates before updating these methods
import xml.etree.ElementTree as ET
from typing import Any, Callable, List, Optional

from .._utils.model_base import Model as _Model, _MyMutableMapping, _RestField, _deserialize


# The original ``Model.__new__`` does ``rf._module = cls.__module__`` which
# lets an external subclass overwrite
# ``_module`` on the *shared* descriptor, corrupting type resolution for
# every class that shares it.  This replacement resolves forward references
# against the module that *defined* the rest_field and uses that class's own
# annotations (not merged subclass annotations) to avoid resolving to a type
# whose ``__init__`` can't handle XML elements.

# TODO: ask the emitter folks
def _patched_new(cls, *args, **kwargs):
    cache_key = f"{cls.__module__}.{cls.__qualname__}"
    if cache_key in cls._calculated:
        return object.__new__(cls)

    # Walk only user-defined classes (base-first), stopping before the
    # framework base.  Each _RestField is configured with the module of
    # the class that defined it so forward references resolve correctly.
    model_index = cls.__mro__.index(_Model)
    attr_to_rest_field: dict[str, _RestField] = {}
    for mro_class in reversed(cls.__mro__[:model_index]):
        annotations = getattr(mro_class, "__annotations__", {})
        for attr, rest_field in mro_class.__dict__.items():
            if attr.startswith("_") or not isinstance(rest_field, _RestField):
                continue

            attr_to_rest_field[attr] = rest_field
            rest_field._module = mro_class.__module__
            if not rest_field._type:
                rest_field._type = rest_field._get_deserialize_callable_from_annotation(annotations.get(attr))
            if not rest_field._rest_name_input:
                rest_field._rest_name_input = attr

    cls._attr_to_rest_field = attr_to_rest_field
    cls._backcompat_attr_to_rest_field = {
        _Model._get_backcompat_attribute_name(attr_to_rest_field, attr): rest_field
        for attr, rest_field in attr_to_rest_field.items()
    }

    # Reverse mapping: REST wire name → Python attribute name
    cls._rest_name_to_attr = {rest_field._rest_name: attr for attr, rest_field in attr_to_rest_field.items()}
    cls._calculated.add(cache_key)

    return object.__new__(cls)

_Model.__new__ = _patched_new


# ---------------------------------------------------------------------------
# Backcompat shims for public methods that existed on the old autorest
# ``msrest.serialization.Model`` base class. The TypeSpec-generated models
# inherit from ``_Model`` (a ``MutableMapping`` subclass) which does not
# expose ``serialize``/``deserialize``/``from_dict``/``validate``/
# ``is_xml_model``/``enable_additional_properties_sending``. Re-adding them
# here preserves backward compatibility for users.
# ---------------------------------------------------------------------------


_original_as_dict = _Model.as_dict


def _remap_keys(d, rest_name_to_attr):
    """Recursively remap REST wire-name keys to Python attribute names."""
    if isinstance(d, dict):
        return {rest_name_to_attr.get(k, k): _remap_keys(v, rest_name_to_attr) for k, v in d.items()}
    if isinstance(d, list):
        return [_remap_keys(item, rest_name_to_attr) for item in d]
    return d


def _patched_as_dict(
    self,
    keep_readonly: bool = True,
    key_transformer: Optional[Callable[[str, dict, Any], Any]] = None,  # pylint: disable=unused-argument
    *,
    exclude_readonly: bool = False,
    **kwargs: Any,
) -> dict:
    """Backcompat wrapper that returns Python attribute names (snake_case).

    Accepts both the old autorest signature (``keep_readonly``,
    ``key_transformer``) and the new TypeSpec keyword-only
    ``exclude_readonly`` parameter.  ``key_transformer`` is accepted for
    signature compatibility but ignored; keys are always remapped to
    Python attribute names.
    """
    kwargs.pop("is_xml", None)
    effective_exclude = exclude_readonly or not keep_readonly
    result = _original_as_dict(self, exclude_readonly=effective_exclude)
    rest_name_to_attr = getattr(type(self), "_rest_name_to_attr", {})
    return _remap_keys(result, rest_name_to_attr)


def _patched_serialize(self, keep_readonly: bool = False, **kwargs: Any) -> dict:
    """Backcompat alias for the old autorest ``Model.serialize``.

    Equivalent to ``as_dict(keep_readonly=keep_readonly)`` with REST wire
    names (camelCase) as keys — matching what the old autorest serializer
    sent to the server.
    """
    kwargs.pop("is_xml", None)
    return _original_as_dict(self, exclude_readonly=not keep_readonly)


def _patched_validate(self) -> list:  # pylint: disable=unused-argument
    """Backcompat no-op for the old autorest ``Model.validate``.

    TypeSpec models do not perform client-side validation; return an empty
    list to match the old "no errors" return value.
    """
    return []


def _patched_deserialize(cls, data: Any, content_type: Optional[str] = None) -> Any:
    """Backcompat classmethod for the old autorest ``Model.deserialize``.

    Accepts either a JSON-compatible dict/str or (when ``content_type`` is
    XML) an XML string or ``ElementTree.Element``.
    """
    if content_type and "xml" in content_type.lower():
        if isinstance(data, (bytes, str)):
            data = ET.fromstring(data)  # nosec
        return cls(data)
    return _deserialize(cls, data)


def _patched_from_dict(
    cls,
    data: Any,
    key_extractors: Optional[Callable[[str, dict, Any], Any]] = None,  # pylint: disable=unused-argument
    content_type: Optional[str] = None,
) -> Any:
    """Backcompat classmethod for the old autorest ``Model.from_dict``.

    ``key_extractors`` is accepted for signature compatibility but ignored;
    the TypeSpec deserializer always uses REST-key mapping.
    """
    if content_type and "xml" in content_type.lower():
        if isinstance(data, (bytes, str)):
            data = ET.fromstring(data)  # nosec
        return cls(data)
    return _deserialize(cls, data)


def _patched_enable_additional_properties_sending(cls) -> None:  # pylint: disable=unused-argument
    """Backcompat no-op for the old autorest ``Model.enable_additional_properties_sending``.

    TypeSpec models already round-trip unknown properties through ``_data``.
    """
    return None


def _patched_is_xml_model(cls) -> bool:
    """Backcompat classmethod for the old autorest ``Model.is_xml_model``.

    Returns True when the model has an ``_xml`` class attribute (set by the
    generator for models that serialize to/from XML).
    """
    return bool(getattr(cls, "_xml", None))

_Model.as_dict = _patched_as_dict
_Model.serialize = _patched_serialize
_Model.validate = _patched_validate
_Model.deserialize = classmethod(_patched_deserialize)
_Model.from_dict = classmethod(_patched_from_dict)
_Model.enable_additional_properties_sending = classmethod(_patched_enable_additional_properties_sending)
_Model.is_xml_model = classmethod(_patched_is_xml_model)


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


__all__: List[str] = []


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
