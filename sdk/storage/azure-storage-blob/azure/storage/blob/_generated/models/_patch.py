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
from typing import Any, List, Mapping, Optional, overload

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
    StorageServiceProperties as _GenStorageServiceProperties,
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


class ArrowField(_AutorestCompatMixin, _GenArrowField):
    """ArrowField with autorest serialization compatibility."""

    _validation = {
        "type": {"required": True},
    }
    _attribute_map = {
        "type": {"key": "Type", "type": "str"},
        "name": {"key": "Name", "type": "str"},
        "precision": {"key": "Precision", "type": "int"},
        "scale": {"key": "Scale", "type": "int"},
    }
    _xml_map = {"name": "Field"}


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


class StaticWebsite(_AutorestCompatMixin, _GenStaticWebsite):
    """StaticWebsite with autorest serialization compatibility."""

    _validation = {
        "enabled": {"required": True},
    }
    _attribute_map = {
        "enabled": {"key": "Enabled", "type": "bool"},
        "index_document": {"key": "IndexDocument", "type": "str"},
        "error_document404_path": {"key": "ErrorDocument404Path", "type": "str"},
        "default_index_document_path": {"key": "DefaultIndexDocumentPath", "type": "str"},
    }


# ---------------------------------------------------------------------------
# Parameter group models
# ---------------------------------------------------------------------------


class AppendPositionAccessConditions(_Model):
    """Parameter group for append position access conditions.

    :ivar max_size: Optional conditional header. The max length in bytes permitted for the append
        blob. If the Append Block operation would cause the blob to exceed that limit or if the
        blob size is already greater than the value specified in this header, the request will fail
        with MaxBlobSizeConditionNotMet error (HTTP status code 412 - Precondition Failed).
    :vartype max_size: int
    :ivar append_position: Optional conditional header, used only for the Append Block operation.
        A number indicating the byte offset to compare. Append Block will succeed only if the
        append position is equal to this number. If it is not, the request will fail with the
        AppendPositionConditionNotMet error (HTTP status code 412 - Precondition Failed).
    :vartype append_position: int
    """

    max_size: Optional[int] = rest_field(name="max_size", visibility=["read", "create", "update", "delete", "query"])
    """Optional conditional header. The max length in bytes permitted for the append blob."""
    append_position: Optional[int] = rest_field(
        name="append_position", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional conditional header, used only for the Append Block operation."""

    @overload
    def __init__(
        self,
        *,
        max_size: Optional[int] = None,
        append_position: Optional[int] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class BlobHTTPHeaders(_Model):
    """Parameter group for blob HTTP headers.

    :ivar blob_cache_control: Optional. Sets the blob's cache control. If specified, this property
        is stored with the blob and returned with a read request.
    :vartype blob_cache_control: str
    :ivar blob_content_type: Optional. Sets the blob's content type. If specified, this property
        is stored with the blob and returned with a read request.
    :vartype blob_content_type: str
    :ivar blob_content_md5: Optional. An MD5 hash of the blob content. Note that this hash is not
        validated, as the hashes for the individual blocks were validated when each was uploaded.
    :vartype blob_content_md5: bytes
    :ivar blob_content_encoding: Optional. Sets the blob's content encoding. If specified, this
        property is stored with the blob and returned with a read request.
    :vartype blob_content_encoding: str
    :ivar blob_content_language: Optional. Set the blob's content language. If specified, this
        property is stored with the blob and returned with a read request.
    :vartype blob_content_language: str
    :ivar blob_content_disposition: Optional. Sets the blob's Content-Disposition header.
    :vartype blob_content_disposition: str
    """

    blob_cache_control: Optional[str] = rest_field(
        name="blob_cache_control", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Sets the blob's cache control."""
    blob_content_type: Optional[str] = rest_field(
        name="blob_content_type", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Sets the blob's content type."""
    blob_content_md5: Optional[bytes] = rest_field(
        name="blob_content_md5", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. An MD5 hash of the blob content."""
    blob_content_encoding: Optional[str] = rest_field(
        name="blob_content_encoding", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Sets the blob's content encoding."""
    blob_content_language: Optional[str] = rest_field(
        name="blob_content_language", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Set the blob's content language."""
    blob_content_disposition: Optional[str] = rest_field(
        name="blob_content_disposition", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Sets the blob's Content-Disposition header."""

    @overload
    def __init__(
        self,
        *,
        blob_cache_control: Optional[str] = None,
        blob_content_type: Optional[str] = None,
        blob_content_md5: Optional[bytes] = None,
        blob_content_encoding: Optional[str] = None,
        blob_content_language: Optional[str] = None,
        blob_content_disposition: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class BlobModifiedAccessConditions(_Model):
    """Parameter group for blob modified access conditions.

    :ivar if_modified_since: Specify this header value to operate only on a blob if it has been
        modified since the specified date/time.
    :vartype if_modified_since: ~datetime.datetime
    :ivar if_unmodified_since: Specify this header value to operate only on a blob if it has not
        been modified since the specified date/time.
    :vartype if_unmodified_since: ~datetime.datetime
    :ivar if_match: Specify an ETag value to operate only on blobs with a matching value.
    :vartype if_match: str
    :ivar if_none_match: Specify an ETag value to operate only on blobs without a matching value.
    :vartype if_none_match: str
    """

    if_modified_since: Optional[datetime.datetime] = rest_field(
        name="if_modified_since", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify this header value to operate only on a blob if it has been modified since the specified date/time."""
    if_unmodified_since: Optional[datetime.datetime] = rest_field(
        name="if_unmodified_since", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify this header value to operate only on a blob if it has not been modified since the specified date/time."""
    if_match: Optional[str] = rest_field(name="if_match", visibility=["read", "create", "update", "delete", "query"])
    """Specify an ETag value to operate only on blobs with a matching value."""
    if_none_match: Optional[str] = rest_field(
        name="if_none_match", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify an ETag value to operate only on blobs without a matching value."""

    @overload
    def __init__(
        self,
        *,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        if_match: Optional[str] = None,
        if_none_match: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ContainerCpkScopeInfo(_Model):
    """Parameter group for container CPK scope info.

    :ivar default_encryption_scope: Optional. Version 2019-07-07 and later. Specifies the default
        encryption scope to set on the container and use for all future writes.
    :vartype default_encryption_scope: str
    :ivar prevent_encryption_scope_override: Optional. Version 2019-07-07 and later. If true,
        prevents any request from specifying a different encryption scope than the scope set on
        the container.
    :vartype prevent_encryption_scope_override: bool
    """

    default_encryption_scope: Optional[str] = rest_field(
        name="default_encryption_scope", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Specifies the default encryption scope to set on the container."""
    prevent_encryption_scope_override: Optional[bool] = rest_field(
        name="prevent_encryption_scope_override", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. If true, prevents any request from specifying a different encryption scope."""

    @overload
    def __init__(
        self,
        *,
        default_encryption_scope: Optional[str] = None,
        prevent_encryption_scope_override: Optional[bool] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CpkScopeInfo(_Model):
    """Parameter group for CPK scope info.

    :ivar encryption_scope: Optional. Version 2019-07-07 and later. Specifies the name of the
        encryption scope to use to encrypt the data provided in the request. If not specified,
        encryption is performed with the default account encryption scope.
    :vartype encryption_scope: str
    """

    encryption_scope: Optional[str] = rest_field(
        name="encryption_scope", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Specifies the name of the encryption scope to use to encrypt the data."""

    @overload
    def __init__(
        self,
        *,
        encryption_scope: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CpkInfo(_Model):
    """Parameter group for CPK info.

    :ivar encryption_key: Optional. Specifies the encryption key to use to encrypt the data
        provided in the request.
    :vartype encryption_key: str
    :ivar encryption_key_sha256: Optional. Specifies the SHA256 hash of the encryption key.
    :vartype encryption_key_sha256: str
    :ivar encryption_algorithm: Optional. Specifies the algorithm to use when encrypting data
        using the given key.
    :vartype encryption_algorithm: str
    """

    encryption_key: Optional[str] = rest_field(
        name="encryption_key", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Specifies the encryption key to use to encrypt the data provided in the request."""
    encryption_key_sha256: Optional[str] = rest_field(
        name="encryption_key_sha256", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Specifies the SHA256 hash of the encryption key."""
    encryption_algorithm: Optional[str] = rest_field(
        name="encryption_algorithm", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Specifies the algorithm to use when encrypting data using the given key."""

    @overload
    def __init__(
        self,
        *,
        encryption_key: Optional[str] = None,
        encryption_key_sha256: Optional[str] = None,
        encryption_algorithm: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModifiedAccessConditions(_Model):
    """Parameter group for modified access conditions.

    :ivar if_modified_since: Specify this header value to operate only on a blob if it has been
        modified since the specified date/time.
    :vartype if_modified_since: ~datetime.datetime
    :ivar if_unmodified_since: Specify this header value to operate only on a blob if it has not
        been modified since the specified date/time.
    :vartype if_unmodified_since: ~datetime.datetime
    :ivar if_match: Specify an ETag value to operate only on blobs with a matching value.
    :vartype if_match: str
    :ivar if_none_match: Specify an ETag value to operate only on blobs without a matching value.
    :vartype if_none_match: str
    :ivar if_tags: Specify a SQL where clause on blob tags to operate only on blobs with a
        matching value.
    :vartype if_tags: str
    """

    if_modified_since: Optional[datetime.datetime] = rest_field(
        name="if_modified_since", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify this header value to operate only on a blob if it has been modified since the specified date/time."""
    if_unmodified_since: Optional[datetime.datetime] = rest_field(
        name="if_unmodified_since", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify this header value to operate only on a blob if it has not been modified since the specified date/time."""
    if_match: Optional[str] = rest_field(name="if_match", visibility=["read", "create", "update", "delete", "query"])
    """Specify an ETag value to operate only on blobs with a matching value."""
    if_none_match: Optional[str] = rest_field(
        name="if_none_match", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify an ETag value to operate only on blobs without a matching value."""
    if_tags: Optional[str] = rest_field(name="if_tags", visibility=["read", "create", "update", "delete", "query"])
    """Specify a SQL where clause on blob tags to operate only on blobs with a matching value."""

    @overload
    def __init__(
        self,
        *,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        if_match: Optional[str] = None,
        if_none_match: Optional[str] = None,
        if_tags: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class SequenceNumberAccessConditions(_Model):
    """Parameter group for sequence number access conditions.

    :ivar if_sequence_number_less_than_or_equal_to: Specify this header value to operate only on a
        blob if it has a sequence number less than or equal to the specified.
    :vartype if_sequence_number_less_than_or_equal_to: int
    :ivar if_sequence_number_less_than: Specify this header value to operate only on a blob if it
        has a sequence number less than the specified.
    :vartype if_sequence_number_less_than: int
    :ivar if_sequence_number_equal_to: Specify this header value to operate only on a blob if it
        has the specified sequence number.
    :vartype if_sequence_number_equal_to: int
    """

    if_sequence_number_less_than_or_equal_to: Optional[int] = rest_field(
        name="if_sequence_number_less_than_or_equal_to", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify this header value to operate only on a blob if it has a sequence number less than or equal to the specified."""
    if_sequence_number_less_than: Optional[int] = rest_field(
        name="if_sequence_number_less_than", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify this header value to operate only on a blob if it has a sequence number less than the specified."""
    if_sequence_number_equal_to: Optional[int] = rest_field(
        name="if_sequence_number_equal_to", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify this header value to operate only on a blob if it has the specified sequence number."""

    @overload
    def __init__(
        self,
        *,
        if_sequence_number_less_than_or_equal_to: Optional[int] = None,
        if_sequence_number_less_than: Optional[int] = None,
        if_sequence_number_equal_to: Optional[int] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class SourceCpkInfo(_Model):
    """Parameter group for source CPK info.

    :ivar source_encryption_key: Optional. Specifies the encryption key to use to decrypt the
        source data.
    :vartype source_encryption_key: str
    :ivar source_encryption_key_sha256: Optional. Specifies the SHA256 hash of the encryption key
        used to decrypt the source data.
    :vartype source_encryption_key_sha256: str
    :ivar source_encryption_algorithm: Optional. Specifies the algorithm to use when decrypting
        the source data using the given key.
    :vartype source_encryption_algorithm: str
    """

    source_encryption_key: Optional[str] = rest_field(
        name="source_encryption_key", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Specifies the encryption key to use to decrypt the source data."""
    source_encryption_key_sha256: Optional[str] = rest_field(
        name="source_encryption_key_sha256", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Specifies the SHA256 hash of the encryption key used to decrypt the source data."""
    source_encryption_algorithm: Optional[str] = rest_field(
        name="source_encryption_algorithm", visibility=["read", "create", "update", "delete", "query"]
    )
    """Optional. Specifies the algorithm to use when decrypting the source data using the given key."""

    @overload
    def __init__(
        self,
        *,
        source_encryption_key: Optional[str] = None,
        source_encryption_key_sha256: Optional[str] = None,
        source_encryption_algorithm: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class SourceModifiedAccessConditions(_Model):
    """Parameter group for source modified access conditions.

    :ivar source_if_modified_since: Specify this header value to operate only on a blob if it has
        been modified since the specified date/time.
    :vartype source_if_modified_since: ~datetime.datetime
    :ivar source_if_unmodified_since: Specify this header value to operate only on a blob if it
        has not been modified since the specified date/time.
    :vartype source_if_unmodified_since: ~datetime.datetime
    :ivar source_if_match: Specify an ETag value to operate only on blobs with a matching value.
    :vartype source_if_match: str
    :ivar source_if_none_match: Specify an ETag value to operate only on blobs without a matching
        value.
    :vartype source_if_none_match: str
    :ivar source_if_tags: Specify a SQL where clause on blob tags to operate only on blobs with a
        matching value.
    :vartype source_if_tags: str
    """

    source_if_modified_since: Optional[datetime.datetime] = rest_field(
        name="source_if_modified_since", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify this header value to operate only on a blob if it has been modified since the specified date/time."""
    source_if_unmodified_since: Optional[datetime.datetime] = rest_field(
        name="source_if_unmodified_since", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify this header value to operate only on a blob if it has not been modified since the specified date/time."""
    source_if_match: Optional[str] = rest_field(
        name="source_if_match", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify an ETag value to operate only on blobs with a matching value."""
    source_if_none_match: Optional[str] = rest_field(
        name="source_if_none_match", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify an ETag value to operate only on blobs without a matching value."""
    source_if_tags: Optional[str] = rest_field(
        name="source_if_tags", visibility=["read", "create", "update", "delete", "query"]
    )
    """Specify a SQL where clause on blob tags to operate only on blobs with a matching value."""

    @overload
    def __init__(
        self,
        *,
        source_if_modified_since: Optional[datetime.datetime] = None,
        source_if_unmodified_since: Optional[datetime.datetime] = None,
        source_if_match: Optional[str] = None,
        source_if_none_match: Optional[str] = None,
        source_if_tags: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class LeaseAccessConditions(_Model):
    """Parameter group for lease access conditions.

    :ivar lease_id: If specified, the operation only succeeds if the resource's lease is active
        and matches this ID.
    :vartype lease_id: str
    """

    lease_id: Optional[str] = rest_field(name="lease_id", visibility=["read", "create", "update", "delete", "query"])
    """If specified, the operation only succeeds if the resource's lease is active and matches this ID."""

    @overload
    def __init__(
        self,
        *,
        lease_id: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


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
    "ModifiedAccessConditions",
    "SequenceNumberAccessConditions",
    "SourceCpkInfo",
    "CpkScopeInfo",
    "SourceModifiedAccessConditions",
    "LeaseAccessConditions",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
