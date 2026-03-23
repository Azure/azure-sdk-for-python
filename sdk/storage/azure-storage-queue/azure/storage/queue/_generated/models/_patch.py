# cod# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import xml.etree.ElementTree as ET
from typing import List

from .._utils.model_base import Model as _Model, _MyMutableMapping, _RestField
from ._models import (
    AccessPolicy as _GenAccessPolicy,
    CorsRule as _GenCorsRule,
    Logging as _GenLogging,
    Metrics as _GenMetrics,
    RetentionPolicy as _GenRetentionPolicy,
)


def _lazy_data_getattr(self, name):
    """Lazily initialize _data for subclasses that skip super().__init__()."""
    if name == "_data":
        object.__setattr__(self, "_data", {})
        return self._data
    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


def _model_setattr(self, name, value):
    """Route attribute writes through _RestField descriptors even when shadowed."""
    if not name.startswith("_"):
        # Walk the MRO looking for a _RestField descriptor that may be shadowed
        for cls in type(self).__mro__:
            member = cls.__dict__.get(name)
            if isinstance(member, _RestField):
                member.__set__(self, value)
                return
    object.__setattr__(self, name, value)


def _model_getattribute(self, name):
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


_MyMutableMapping.__getattr__ = _lazy_data_getattr
_MyMutableMapping.__setattr__ = _model_setattr
_MyMutableMapping.__getattribute__ = _model_getattribute


# ---------------------------------------------------------------------------
# Fix Model.__new__ to resolve _RestField forward references against the
# module that *defined* the field, not whichever subclass is instantiated
# first.  The original code does ``rf._module = cls.__module__`` which lets
# an external subclass (e.g. from azure-storage-file-datalake) overwrite
# _module on the shared descriptor, corrupting type resolution for everyone.
# ---------------------------------------------------------------------------
_orig_model_new = _Model.__new__


def _patched_model_new(cls, *args, **kwargs):
    if f"{cls.__module__}.{cls.__qualname__}" not in cls._calculated:
        mros = cls.__mro__[:-9][::-1]
        attr_to_rest_field = {}
        # Track which MRO class defined each rest_field so we resolve
        # forward references against the *defining* module, not cls.
        attr_to_defining_class = {}
        for mro_class in mros:
            for k, v in mro_class.__dict__.items():
                if k[0] != "_" and hasattr(v, "_type"):
                    attr_to_rest_field[k] = v
                    attr_to_defining_class[k] = mro_class

        annotations = {
            k: v
            for mro_class in mros
            if hasattr(mro_class, "__annotations__")
            for k, v in mro_class.__annotations__.items()
        }
        for attr, rf in attr_to_rest_field.items():
            # Use the defining class's module for forward-ref resolution
            defining_cls = attr_to_defining_class[attr]
            rf._module = defining_cls.__module__
            if not rf._type:
                rf._type = rf._get_deserialize_callable_from_annotation(annotations.get(attr, None))
            if not rf._rest_name_input:
                rf._rest_name_input = attr
        cls._attr_to_rest_field = dict(attr_to_rest_field.items())
        cls._backcompat_attr_to_rest_field = {
            _Model._get_backcompat_attribute_name(cls._attr_to_rest_field, attr): rf
            for attr, rf in cls._attr_to_rest_field.items()
        }
        cls._calculated.add(f"{cls.__module__}.{cls.__qualname__}")

    return object.__new__(cls)


_Model.__new__ = _patched_model_new


# ---------------------------------------------------------------------------
# Autorest serialization compatibility layer
# ---------------------------------------------------------------------------
# The old autorest serialization pipeline (Serializer/Deserializer from
# _utils.serialization) relies on class-level _attribute_map, _validation,
# _xml_map, is_xml_model(), and _create_xml_node() — none of which exist on
# the new model_base.Model subclasses.  The wrappers below add exactly those
# attributes so that the operations code can keep serializing/deserializing
# them unchanged.
# ---------------------------------------------------------------------------


def _create_xml_node(tag, prefix=None, ns=None):
    if prefix and ns:
        ET.register_namespace(prefix, ns)
    if ns:
        return ET.Element("{" + ns + "}" + tag)
    return ET.Element(tag)


class _AutorestCompatMixin:
    """Adds msrest-style (de)serialization hooks to ``model_base.Model`` subclasses."""

    _attribute_map: dict = {}
    _validation: dict = {}

    @classmethod
    def is_xml_model(cls) -> bool:
        return bool(getattr(cls, "_xml_map", None))

    @classmethod
    def _create_xml_node(cls):
        xml_map = getattr(cls, "_xml_map", {})
        return _create_xml_node(
            xml_map.get("name", cls.__name__),
            xml_map.get("prefix"),
            xml_map.get("ns"),
        )


class AccessPolicy(_AutorestCompatMixin, _GenAccessPolicy):
    """AccessPolicy with autorest serialization compatibility."""

    _attribute_map = {
        "start": {"key": "Start", "type": "str"},
        "expiry": {"key": "Expiry", "type": "str"},
        "permission": {"key": "Permission", "type": "str"},
    }


class CorsRule(_AutorestCompatMixin, _GenCorsRule):
    """CorsRule with autorest serialization compatibility."""

    _validation = {
        "allowed_origins": {"required": True},
        "allowed_methods": {"required": True},
        "allowed_headers": {"required": True},
        "exposed_headers": {"required": True},
        "max_age_in_seconds": {"required": True, "minimum": 0},
    }
    _attribute_map = {
        "allowed_origins": {"key": "AllowedOrigins", "type": "str"},
        "allowed_methods": {"key": "AllowedMethods", "type": "str"},
        "allowed_headers": {"key": "AllowedHeaders", "type": "str"},
        "exposed_headers": {"key": "ExposedHeaders", "type": "str"},
        "max_age_in_seconds": {"key": "MaxAgeInSeconds", "type": "int"},
    }


class Logging(_AutorestCompatMixin, _GenLogging):
    """Logging with autorest serialization compatibility."""

    _validation = {
        "version": {"required": True},
        "delete": {"required": True},
        "read": {"required": True},
        "write": {"required": True},
        "retention_policy": {"required": True},
    }
    _attribute_map = {
        "version": {"key": "Version", "type": "str"},
        "delete": {"key": "Delete", "type": "bool"},
        "read": {"key": "Read", "type": "bool"},
        "write": {"key": "Write", "type": "bool"},
        "retention_policy": {"key": "RetentionPolicy", "type": "RetentionPolicy"},
    }


class Metrics(_AutorestCompatMixin, _GenMetrics):
    """Metrics with autorest serialization compatibility."""

    _validation = {
        "enabled": {"required": True},
    }
    _attribute_map = {
        "version": {"key": "Version", "type": "str"},
        "enabled": {"key": "Enabled", "type": "bool"},
        "include_apis": {"key": "IncludeAPIs", "type": "bool"},
        "retention_policy": {"key": "RetentionPolicy", "type": "RetentionPolicy"},
    }


class RetentionPolicy(_AutorestCompatMixin, _GenRetentionPolicy):
    """RetentionPolicy with autorest serialization compatibility."""

    _validation = {
        "enabled": {"required": True},
        "days": {"minimum": 1},
    }
    _attribute_map = {
        "enabled": {"key": "Enabled", "type": "bool"},
        "days": {"key": "Days", "type": "int"},
        "allow_permanent_delete": {"key": "AllowPermanentDelete", "type": "bool"},
    }

__all__: List[str] = [
    "AccessPolicy",
    "CorsRule",
    "Logging",
    "Metrics",
    "RetentionPolicy",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """