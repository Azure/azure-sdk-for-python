# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
import xml.etree.ElementTree as ET
from typing import Any, Callable, List, Optional

from .._utils.model_base import Model as _Model, rest_field, _MyMutableMapping, _RestField, _deserialize


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


# ---------------------------------------------------------------------------
# Backcompat shims for public methods that existed on the old autorest
# ``msrest.serialization.Model`` base class.  The TypeSpec-generated models
# inherit from ``_Model`` (a ``MutableMapping`` subclass) which does not
# expose ``serialize``/``deserialize``/``from_dict``/``validate``/
# ``is_xml_model``/``enable_additional_properties_sending``.  Re-adding them
# here preserves backward compatibility for users (e.g. azure-storage-file-
# datalake) that still call these methods on models re-exported from
# azure-storage-blob.
# ---------------------------------------------------------------------------


_original_as_dict = _Model.as_dict


def _patched_as_dict(
    self,
    keep_readonly: bool = True,
    key_transformer: Optional[Callable[[str, dict, Any], Any]] = None,  # pylint: disable=unused-argument
    **kwargs: Any,
) -> dict:
    """Backcompat alias for the old autorest ``Model.as_dict``.

    The TypeSpec base ``Model.as_dict`` only accepts ``exclude_readonly``.
    Older autorest callers may pass ``keep_readonly`` and/or
    ``key_transformer``; map those to the new signature (``key_transformer``
    is ignored because the generated TypeSpec dict already uses REST keys).
    """
    # Ignore other autorest-only kwargs (e.g. is_xml) that don't apply here.
    kwargs.pop("is_xml", None)
    return _original_as_dict(self, exclude_readonly=not keep_readonly)


def _patched_serialize(self, keep_readonly: bool = False, **kwargs: Any) -> dict:
    """Backcompat alias for the old autorest ``Model.serialize``.

    Equivalent to ``as_dict(keep_readonly=keep_readonly)`` for JSON payloads.
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
            parser = ET.XMLParser()
            parser.feed(data if isinstance(data, str) else data.decode("utf-8"))
            data = parser.close()
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
            parser = ET.XMLParser()
            parser.feed(data if isinstance(data, str) else data.decode("utf-8"))
            data = parser.close()
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


__all__: List[str] = ["_Model"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
