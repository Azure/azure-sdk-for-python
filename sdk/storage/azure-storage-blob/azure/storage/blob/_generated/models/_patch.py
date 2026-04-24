# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import xml.etree.ElementTree as ET
from typing import Any, Callable, List, Optional

from .._utils.model_base import Model as _Model, _MyMutableMapping, _RestField, _deserialize, _UNSET


def _patched_getattr(self, name):
    """Lazily initialize _data for subclasses that skip super().__init__()."""
    if name == "_data":
        object.__setattr__(self, "_data", {})
        return self._data
    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


def _patched_setattr(self, name, value):
    """Route attribute writes through _RestField descriptors even when shadowed.

    Only installed on classes whose subclass-level annotations shadow a parent's
    ``_RestField`` (see ``_patched_new``). For non-shadowing classes (the entire
    generated TypeSpec model graph) this override is *not* installed, so writes
    use native ``object.__setattr__``.
    """
    cls = type(self)
    if not name.startswith("_") and name in cls._shadowed_rest_fields:
        rf = cls._attr_to_rest_field.get(name)
        if rf is not None:
            rf.__set__(self, value)
            return
    object.__setattr__(self, name, value)


def _patched_getattribute(self, name):
    """Route attribute reads through _RestField descriptors even when shadowed.

    Only installed on classes whose subclass-level annotations shadow a parent's
    ``_RestField``. The hot list-blobs path operates on generated classes that
    do *not* have shadowing, so this override is not installed there and they
    use native C ``object.__getattribute__``.
    """
    if not name.startswith("_"):
        cls = type(self)
        if name in cls._shadowed_rest_fields:
            rf = cls._attr_to_rest_field.get(name)
            if rf is not None:
                return rf.__get__(self, cls)
    return object.__getattribute__(self, name)


# The original ``Model.__new__`` does ``rf._module = cls.__module__`` which
# lets an external subclass (e.g. from azure-storage-file-datalake) overwrite
# ``_module`` on the *shared* descriptor, corrupting type resolution for
# every class that shares it.  This replacement resolves forward references
# against the module that *defined* the rest_field and uses that class's own
# annotations (not merged subclass annotations) to avoid resolving to a type
# whose ``__init__`` can't handle XML elements.


def _patched_new(cls, *args, **kwargs):
    if not cls.__dict__.get("_calculated_done", False):
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
                    if not v._rest_name:
                        v._rest_name = k

        cls._attr_to_rest_field = attr_to_rest_field
        cls._backcompat_attr_to_rest_field = {
            _Model._get_backcompat_attribute_name(cls._attr_to_rest_field, attr): rf
            for attr, rf in cls._attr_to_rest_field.items()
        }

        # Precompute the default-value dict once per class. Model.__init__ copies this
        # per instance instead of rebuilding it from _attr_to_rest_field every call.
        cls._defaults = {
            rf._rest_name: rf._default
            for rf in attr_to_rest_field.values()
            if rf._default is not _UNSET
        }

        # Reverse mapping: REST wire name → Python attribute name
        cls._rest_name_to_attr = {
            rf._rest_name: attr for attr, rf in attr_to_rest_field.items()
        }

        # Detect attrs whose value in the MRO is *not* a _RestField but which
        # *do* have a _RestField further up the MRO. Those are the only attrs
        # for which the patched dunders actually need to reroute: normal
        # Python descriptor semantics already cover non-shadowed attrs.
        # Generated TypeSpec models have no shadowing.
        shadowed: set = set()
        for attr in attr_to_rest_field:
            for c in cls.__mro__:
                if attr in c.__dict__:
                    if not isinstance(c.__dict__[attr], _RestField):
                        shadowed.add(attr)
                    break
        cls._shadowed_rest_fields = shadowed

        # Always install ``__getattr__`` for lazy ``_data`` initialization.
        # Some hand-written subclasses (e.g. CorsRule, BlobAnalyticsLogging,
        # Metrics, StaticWebsite) override ``__init__`` without calling
        # ``super().__init__()``, so ``_data`` is never created by the
        # framework. ``__getattr__`` is only invoked when normal attribute
        # lookup misses, so it does NOT disable CPython's C-level fast path
        # for ordinary reads -- it costs effectively nothing on the hot path.
        cls.__getattr__ = _patched_getattr

        # Install ``__getattribute__``/``__setattr__`` ONLY on classes that
        # actually shadow a parent ``_RestField`` with a non-descriptor class
        # attribute. Installing ``__getattribute__`` (even a trivial one)
        # disables CPython's C-level attribute access fast path for every
        # instance of that class -- the difference is dramatic on the
        # list-blobs hot path which makes tens of thousands of reads per
        # call against generated models. Installing only on shadowing
        # subclasses (e.g. RetentionPolicy, StaticWebsite, BlobAnalyticsLogging,
        # Metrics) preserves backcompat semantics where they are needed
        # without paying the cost everywhere.
        if shadowed:
            cls.__setattr__ = _patched_setattr
            cls.__getattribute__ = _patched_getattribute

        cls._calculated_done = True

    return object.__new__(cls)


_Model.__new__ = _patched_new


# ---------------------------------------------------------------------------
# Backcompat shims for public methods that existed on the old autorest
# ``msrest.serialization.Model`` base class. The TypeSpec-generated models
# inherit from ``_Model`` (a ``MutableMapping`` subclass) which does not
# expose ``serialize``/``deserialize``/``from_dict``/``validate``/
# ``is_xml_model``/``enable_additional_properties_sending``. Re-adding them
# here preserves backward compatibility for users (e.g. azure-storage-file-
# datalake) that still call these methods on models re-exported from
# azure-storage-blob.
# ---------------------------------------------------------------------------


_original_as_dict = _Model.as_dict


def _remap_keys(d, rest_name_to_attr):
    """Recursively remap REST wire-name keys to Python attribute names."""
    if isinstance(d, dict):
        return {
            rest_name_to_attr.get(k, k): _remap_keys(v, rest_name_to_attr)
            for k, v in d.items()
        }
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


__all__: List[str] = []


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
