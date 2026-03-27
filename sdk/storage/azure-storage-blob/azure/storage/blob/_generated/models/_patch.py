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
from typing import Any, List, Optional

from .._utils.model_base import Model as _Model, rest_field, _MyMutableMapping, _RestField
from ._models import (
    BlobItem as BlobItemInternal,
    AccessPolicy as _GenAccessPolicy,
    ArrowField as _GenArrowField,
    CorsRule as _GenCorsRule,
    Logging as _GenLogging,
    Metrics as _GenMetrics,
    RetentionPolicy as _GenRetentionPolicy,
    StaticWebsite as _GenStaticWebsite,
)


def _patched_getattr(self, name):
    """Lazily initialize _data for subclasses that skip super().__init__()."""
    if name == "_data":
        object.__setattr__(self, "_data", {})
        return self._data
    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


def _patched_setattr(self, name, value):
    """Route attribute writes through _RestField descriptors even when shadowed."""
    if not name.startswith("_"):
        for cls in type(self).__mro__:
            member = cls.__dict__.get(name)
            if isinstance(member, _RestField):
                member.__set__(self, value)
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
        mros = cls.__mro__[:-9][::-1]
        attr_to_rest_field = {}
        attr_to_defining_class = {}
        for mro_class in mros:
            for k, v in mro_class.__dict__.items():
                if k[0] != "_" and hasattr(v, "_type"):
                    attr_to_rest_field[k] = v
                    attr_to_defining_class[k] = mro_class

        for attr, rf in attr_to_rest_field.items():
            defining_cls = attr_to_defining_class[attr]
            rf._module = defining_cls.__module__
            if not rf._type:
                defining_annotations = getattr(defining_cls, "__annotations__", {})
                rf._type = rf._get_deserialize_callable_from_annotation(defining_annotations.get(attr, None))
            if not rf._rest_name_input:
                rf._rest_name_input = attr
        cls._attr_to_rest_field = dict(attr_to_rest_field.items())
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


# The old autorest Serializer/Deserializer relies on class-level
# ``_attribute_map``, ``_validation``, ``_xml_map``, ``is_xml_model()``, and
# ``_create_xml_node()`` — none of which exist on the new model_base.Model
# subclasses.  The mixin and wrapper classes below add exactly those
# attributes so the operations code can keep serializing/deserializing them.


def _create_xml_node(tag, prefix=None, ns=None):
    if prefix and ns:
        ET.register_namespace(prefix, ns)
    if ns:
        return ET.Element("{" + ns + "}" + tag)
    return ET.Element(tag)


class _AutorestCompatMixin:
    """Adds msrest-style (de)serialization hooks to model_base.Model subclasses."""

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
    _attribute_map = {
        "start": {"key": "Start", "type": "str"},
        "expiry": {"key": "Expiry", "type": "str"},
        "permission": {"key": "Permission", "type": "str"},
    }


class ArrowField(_AutorestCompatMixin, _GenArrowField):
    _validation = {"type": {"required": True}}
    _attribute_map = {
        "type": {"key": "Type", "type": "str"},
        "name": {"key": "Name", "type": "str"},
        "precision": {"key": "Precision", "type": "int"},
        "scale": {"key": "Scale", "type": "int"},
    }
    _xml_map = {"name": "Field"}


class CorsRule(_AutorestCompatMixin, _GenCorsRule):
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
    _validation = {"enabled": {"required": True}}
    _attribute_map = {
        "version": {"key": "Version", "type": "str"},
        "enabled": {"key": "Enabled", "type": "bool"},
        "include_apis": {"key": "IncludeAPIs", "type": "bool"},
        "retention_policy": {"key": "RetentionPolicy", "type": "RetentionPolicy"},
    }


class RetentionPolicy(_AutorestCompatMixin, _GenRetentionPolicy):
    _validation = {"enabled": {"required": True}, "days": {"minimum": 1}}
    _attribute_map = {
        "enabled": {"key": "Enabled", "type": "bool"},
        "days": {"key": "Days", "type": "int"},
        "allow_permanent_delete": {"key": "AllowPermanentDelete", "type": "bool"},
    }


class StaticWebsite(_AutorestCompatMixin, _GenStaticWebsite):
    _validation = {"enabled": {"required": True}}
    _attribute_map = {
        "enabled": {"key": "Enabled", "type": "bool"},
        "index_document": {"key": "IndexDocument", "type": "str"},
        "error_document404_path": {"key": "ErrorDocument404Path", "type": "str"},
        "default_index_document_path": {"key": "DefaultIndexDocumentPath", "type": "str"},
    }


# Bringing back the parameter group models that were in the old generated code

_ALL_VISIBILITY = ["read", "create", "update", "delete", "query"]


class AppendPositionAccessConditions(_Model):
    max_size: Optional[int] = rest_field(name="max_size", visibility=_ALL_VISIBILITY)
    append_position: Optional[int] = rest_field(name="append_position", visibility=_ALL_VISIBILITY)


class BlobHTTPHeaders(_Model):
    blob_cache_control: Optional[str] = rest_field(name="blob_cache_control", visibility=_ALL_VISIBILITY)
    blob_content_type: Optional[str] = rest_field(name="blob_content_type", visibility=_ALL_VISIBILITY)
    blob_content_md5: Optional[bytes] = rest_field(name="blob_content_md5", visibility=_ALL_VISIBILITY)
    blob_content_encoding: Optional[str] = rest_field(name="blob_content_encoding", visibility=_ALL_VISIBILITY)
    blob_content_language: Optional[str] = rest_field(name="blob_content_language", visibility=_ALL_VISIBILITY)
    blob_content_disposition: Optional[str] = rest_field(name="blob_content_disposition", visibility=_ALL_VISIBILITY)


class BlobModifiedAccessConditions(_Model):
    if_modified_since: Optional[datetime.datetime] = rest_field(name="if_modified_since", visibility=_ALL_VISIBILITY)
    if_unmodified_since: Optional[datetime.datetime] = rest_field(
        name="if_unmodified_since", visibility=_ALL_VISIBILITY
    )
    if_match: Optional[str] = rest_field(name="if_match", visibility=_ALL_VISIBILITY)
    if_none_match: Optional[str] = rest_field(name="if_none_match", visibility=_ALL_VISIBILITY)


class ContainerCpkScopeInfo(_Model):
    default_encryption_scope: Optional[str] = rest_field(name="default_encryption_scope", visibility=_ALL_VISIBILITY)
    prevent_encryption_scope_override: Optional[bool] = rest_field(
        name="prevent_encryption_scope_override", visibility=_ALL_VISIBILITY
    )


class CpkScopeInfo(_Model):
    encryption_scope: Optional[str] = rest_field(name="encryption_scope", visibility=_ALL_VISIBILITY)


class CpkInfo(_Model):
    encryption_key: Optional[str] = rest_field(name="encryption_key", visibility=_ALL_VISIBILITY)
    encryption_key_sha256: Optional[str] = rest_field(name="encryption_key_sha256", visibility=_ALL_VISIBILITY)
    encryption_algorithm: Optional[str] = rest_field(name="encryption_algorithm", visibility=_ALL_VISIBILITY)


class ModifiedAccessConditions(_Model):
    if_modified_since: Optional[datetime.datetime] = rest_field(name="if_modified_since", visibility=_ALL_VISIBILITY)
    if_unmodified_since: Optional[datetime.datetime] = rest_field(
        name="if_unmodified_since", visibility=_ALL_VISIBILITY
    )
    if_match: Optional[str] = rest_field(name="if_match", visibility=_ALL_VISIBILITY)
    if_none_match: Optional[str] = rest_field(name="if_none_match", visibility=_ALL_VISIBILITY)
    if_tags: Optional[str] = rest_field(name="if_tags", visibility=_ALL_VISIBILITY)


class SequenceNumberAccessConditions(_Model):
    if_sequence_number_less_than_or_equal_to: Optional[int] = rest_field(
        name="if_sequence_number_less_than_or_equal_to", visibility=_ALL_VISIBILITY
    )
    if_sequence_number_less_than: Optional[int] = rest_field(
        name="if_sequence_number_less_than", visibility=_ALL_VISIBILITY
    )
    if_sequence_number_equal_to: Optional[int] = rest_field(
        name="if_sequence_number_equal_to", visibility=_ALL_VISIBILITY
    )


class SourceCpkInfo(_Model):
    source_encryption_key: Optional[str] = rest_field(name="source_encryption_key", visibility=_ALL_VISIBILITY)
    source_encryption_key_sha256: Optional[str] = rest_field(
        name="source_encryption_key_sha256", visibility=_ALL_VISIBILITY
    )
    source_encryption_algorithm: Optional[str] = rest_field(
        name="source_encryption_algorithm", visibility=_ALL_VISIBILITY
    )


class SourceModifiedAccessConditions(_Model):
    source_if_modified_since: Optional[datetime.datetime] = rest_field(
        name="source_if_modified_since", visibility=_ALL_VISIBILITY
    )
    source_if_unmodified_since: Optional[datetime.datetime] = rest_field(
        name="source_if_unmodified_since", visibility=_ALL_VISIBILITY
    )
    source_if_match: Optional[str] = rest_field(name="source_if_match", visibility=_ALL_VISIBILITY)
    source_if_none_match: Optional[str] = rest_field(name="source_if_none_match", visibility=_ALL_VISIBILITY)
    source_if_tags: Optional[str] = rest_field(name="source_if_tags", visibility=_ALL_VISIBILITY)


class LeaseAccessConditions(_Model):
    lease_id: Optional[str] = rest_field(name="lease_id", visibility=_ALL_VISIBILITY)


__all__: List[str] = [
    "AccessPolicy",
    "ArrowField",
    "CorsRule",
    "Logging",
    "Metrics",
    "RetentionPolicy",
    "StaticWebsite",
    "AppendPositionAccessConditions",
    "BlobHTTPHeaders",
    "BlobItemInternal",
    "BlobModifiedAccessConditions",
    "ContainerCpkScopeInfo",
    "CpkInfo",
    "CpkScopeInfo",
    "ModifiedAccessConditions",
    "SequenceNumberAccessConditions",
    "SourceCpkInfo",
    "SourceModifiedAccessConditions",
    "LeaseAccessConditions",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
