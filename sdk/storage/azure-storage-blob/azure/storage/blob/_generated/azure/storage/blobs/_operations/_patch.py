# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Mapping, Optional

from azure.core import MatchConditions

from ..models import (
    AppendPositionAccessConditions,
    BlobHTTPHeaders,
    BlobModifiedAccessConditions,
    ContainerCpkScopeInfo,
    CpkInfo,
    CpkScopeInfo,
    LeaseAccessConditions,
    ModifiedAccessConditions,
    SequenceNumberAccessConditions,
    SourceCpkInfo,
    SourceModifiedAccessConditions,
)


def _convert_to_etag_match_condition(
    if_match: Optional[str],
    if_none_match: Optional[str],
    kwargs: dict[str, Any],
) -> None:
    """Convert if_match/if_none_match to etag/match_condition for the new generated operations.

    The old API used if_match and if_none_match directly, but the new generated code
    uses etag and match_condition (from azure.core.MatchConditions) which are then
    converted internally via prep_if_match/prep_if_none_match.

    Conversion logic:
    - if_match with a specific etag -> etag=value, match_condition=IfNotModified
    - if_match='*' -> match_condition=IfPresent
    - if_none_match with a specific etag -> etag=value, match_condition=IfModified
    - if_none_match='*' -> match_condition=IfMissing
    """
    if if_match is not None and kwargs.get("etag") is None:
        if if_match == "*":
            kwargs["match_condition"] = MatchConditions.IfPresent
        else:
            kwargs["etag"] = if_match
            kwargs["match_condition"] = MatchConditions.IfNotModified

    if if_none_match is not None and kwargs.get("etag") is None:
        if if_none_match == "*":
            kwargs["match_condition"] = MatchConditions.IfMissing
        else:
            kwargs["etag"] = if_none_match
            kwargs["match_condition"] = MatchConditions.IfModified


def _set_if_not_none(kwargs: dict[str, Any], key: str, value: Any) -> None:
    """Set a value in kwargs only if the value is not None and the key is not already set."""
    if value is not None and kwargs.get(key) is None:
        kwargs[key] = value


def _extract_blob_http_headers(
    blob_http_headers: Optional[BlobHTTPHeaders],
    kwargs: dict[str, Any],
) -> None:
    """Extract BlobHTTPHeaders fields into kwargs if not already set."""
    if blob_http_headers is not None:
        _set_if_not_none(kwargs, "blob_cache_control", getattr(blob_http_headers, "blob_cache_control", None))
        _set_if_not_none(kwargs, "blob_content_type", getattr(blob_http_headers, "blob_content_type", None))
        _set_if_not_none(kwargs, "blob_content_md5", getattr(blob_http_headers, "blob_content_md5", None))
        _set_if_not_none(kwargs, "blob_content_encoding", getattr(blob_http_headers, "blob_content_encoding", None))
        _set_if_not_none(kwargs, "blob_content_language", getattr(blob_http_headers, "blob_content_language", None))
        _set_if_not_none(kwargs, "blob_content_disposition", getattr(blob_http_headers, "blob_content_disposition", None))


def _extract_lease_access_conditions(
    lease_access_conditions: Optional[LeaseAccessConditions],
    kwargs: dict[str, Any],
) -> None:
    """Extract LeaseAccessConditions fields into kwargs if not already set."""
    if lease_access_conditions is not None:
        _set_if_not_none(kwargs, "lease_id", getattr(lease_access_conditions, "lease_id", None))


def _extract_cpk_info(
    cpk_info: Optional[CpkInfo],
    kwargs: dict[str, Any],
) -> None:
    """Extract CpkInfo fields into kwargs if not already set."""
    if cpk_info is not None:
        _set_if_not_none(kwargs, "encryption_key", getattr(cpk_info, "encryption_key", None))
        _set_if_not_none(kwargs, "encryption_key_sha256", getattr(cpk_info, "encryption_key_sha256", None))
        _set_if_not_none(kwargs, "encryption_algorithm", getattr(cpk_info, "encryption_algorithm", None))


def _extract_cpk_scope_info(
    cpk_scope_info: Optional[CpkScopeInfo],
    kwargs: dict[str, Any],
) -> None:
    """Extract CpkScopeInfo fields into kwargs if not already set."""
    if cpk_scope_info is not None:
        _set_if_not_none(kwargs, "encryption_scope", getattr(cpk_scope_info, "encryption_scope", None))


def _extract_modified_access_conditions(
    modified_access_conditions: Optional[ModifiedAccessConditions],
    kwargs: dict[str, Any],
) -> None:
    """Extract ModifiedAccessConditions fields into kwargs if not already set."""
    if modified_access_conditions is not None:
        _set_if_not_none(kwargs, "if_modified_since", getattr(modified_access_conditions, "if_modified_since", None))
        _set_if_not_none(kwargs, "if_unmodified_since", getattr(modified_access_conditions, "if_unmodified_since", None))
        _set_if_not_none(kwargs, "if_tags", getattr(modified_access_conditions, "if_tags", None))
        # Convert if_match/if_none_match to etag/match_condition
        _convert_to_etag_match_condition(
            getattr(modified_access_conditions, "if_match", None),
            getattr(modified_access_conditions, "if_none_match", None),
            kwargs,
        )


def _extract_source_modified_access_conditions(
    source_modified_access_conditions: Optional[SourceModifiedAccessConditions],
    kwargs: dict[str, Any],
) -> None:
    """Extract SourceModifiedAccessConditions fields into kwargs if not already set."""
    if source_modified_access_conditions is not None:
        _set_if_not_none(
            kwargs, "source_if_modified_since", getattr(source_modified_access_conditions, "source_if_modified_since", None)
        )
        _set_if_not_none(
            kwargs, "source_if_unmodified_since", getattr(source_modified_access_conditions, "source_if_unmodified_since", None)
        )
        _set_if_not_none(kwargs, "source_if_tags", getattr(source_modified_access_conditions, "source_if_tags", None))
        # Pass source_if_match and source_if_none_match directly (they are used as-is in the generated code)
        _set_if_not_none(kwargs, "source_if_match", getattr(source_modified_access_conditions, "source_if_match", None))
        _set_if_not_none(kwargs, "source_if_none_match", getattr(source_modified_access_conditions, "source_if_none_match", None))


def _extract_source_cpk_info(
    source_cpk_info: Optional[SourceCpkInfo],
    kwargs: dict[str, Any],
) -> None:
    """Extract SourceCpkInfo fields into kwargs if not already set."""
    if source_cpk_info is not None:
        _set_if_not_none(kwargs, "source_encryption_key", getattr(source_cpk_info, "source_encryption_key", None))
        _set_if_not_none(kwargs, "source_encryption_key_sha256", getattr(source_cpk_info, "source_encryption_key_sha256", None))
        _set_if_not_none(kwargs, "source_encryption_algorithm", getattr(source_cpk_info, "source_encryption_algorithm", None))


def _extract_sequence_number_access_conditions(
    sequence_number_access_conditions: Optional[SequenceNumberAccessConditions],
    kwargs: dict[str, Any],
) -> None:
    """Extract SequenceNumberAccessConditions fields into kwargs if not already set."""
    if sequence_number_access_conditions is not None:
        _set_if_not_none(
            kwargs,
            "if_sequence_number_less_than_or_equal_to",
            getattr(sequence_number_access_conditions, "if_sequence_number_less_than_or_equal_to", None),
        )
        _set_if_not_none(
            kwargs,
            "if_sequence_number_less_than",
            getattr(sequence_number_access_conditions, "if_sequence_number_less_than", None),
        )
        _set_if_not_none(
            kwargs, "if_sequence_number_equal_to", getattr(sequence_number_access_conditions, "if_sequence_number_equal_to", None)
        )


def _extract_append_position_access_conditions(
    append_position_access_conditions: Optional[AppendPositionAccessConditions],
    kwargs: dict[str, Any],
) -> None:
    """Extract AppendPositionAccessConditions fields into kwargs if not already set."""
    if append_position_access_conditions is not None:
        _set_if_not_none(kwargs, "max_size", getattr(append_position_access_conditions, "max_size", None))
        _set_if_not_none(kwargs, "append_position", getattr(append_position_access_conditions, "append_position", None))


def _extract_container_cpk_scope_info(
    container_cpk_scope_info: Optional[ContainerCpkScopeInfo],
    kwargs: dict[str, Any],
) -> None:
    """Extract ContainerCpkScopeInfo fields into kwargs if not already set."""
    if container_cpk_scope_info is not None:
        _set_if_not_none(kwargs, "default_encryption_scope", getattr(container_cpk_scope_info, "default_encryption_scope", None))
        _set_if_not_none(
            kwargs,
            "prevent_encryption_scope_override",
            getattr(container_cpk_scope_info, "prevent_encryption_scope_override", None),
        )


def _extract_blob_modified_access_conditions(
    blob_modified_access_conditions: Optional[BlobModifiedAccessConditions],
    kwargs: dict[str, Any],
) -> None:
    """Extract BlobModifiedAccessConditions fields into kwargs if not already set."""
    if blob_modified_access_conditions is not None:
        _set_if_not_none(kwargs, "if_modified_since", getattr(blob_modified_access_conditions, "if_modified_since", None))
        _set_if_not_none(kwargs, "if_unmodified_since", getattr(blob_modified_access_conditions, "if_unmodified_since", None))
        # Convert if_match/if_none_match to etag/match_condition
        _convert_to_etag_match_condition(
            getattr(blob_modified_access_conditions, "if_match", None),
            getattr(blob_modified_access_conditions, "if_none_match", None),
            kwargs,
        )


def _remap_parameter_names(kwargs: dict[str, Any]) -> None:
    """Remap old-style parameter names to new generated API parameter names.

    The TypeSpec-generated code uses different parameter names than the old autorest-generated code.
    This function handles the translation so callers using the old names still work.
    """
    # blob_content_length -> size (for PageBlobClient.create)
    if "blob_content_length" in kwargs and "size" not in kwargs:
        kwargs["size"] = kwargs.pop("blob_content_length")

    # # content_length is no longer accepted as a kwarg in most generated methods
    # # (it's calculated internally or is a keyword-only arg). Remove if 0 (page blob create pattern).
    # if "content_length" in kwargs and kwargs["content_length"] == 0:
    #     kwargs.pop("content_length")  # TODO: tldr on this one


def extract_parameter_groups(kwargs: dict[str, Any]) -> None:
    """
    Extract all parameter group objects from kwargs and flatten their fields.

    This function supports backward compatibility with the old API that accepted
    parameter group objects like BlobHTTPHeaders, LeaseAccessConditions, etc.
    """
    # Remap old parameter names to new ones
    _remap_parameter_names(kwargs)

    # Extract and remove parameter groups from kwargs
    blob_http_headers = kwargs.pop("blob_http_headers", None)
    lease_access_conditions = kwargs.pop("lease_access_conditions", None)
    cpk_info = kwargs.pop("cpk_info", None)
    cpk_scope_info = kwargs.pop("cpk_scope_info", None)
    modified_access_conditions = kwargs.pop("modified_access_conditions", None)
    source_modified_access_conditions = kwargs.pop("source_modified_access_conditions", None)
    source_cpk_info = kwargs.pop("source_cpk_info", None)
    sequence_number_access_conditions = kwargs.pop("sequence_number_access_conditions", None)
    append_position_access_conditions = kwargs.pop("append_position_access_conditions", None)
    container_cpk_scope_info = kwargs.pop("container_cpk_scope_info", None)
    blob_modified_access_conditions = kwargs.pop("blob_modified_access_conditions", None)

    # Extract fields from each parameter group
    _extract_blob_http_headers(blob_http_headers, kwargs)
    _extract_lease_access_conditions(lease_access_conditions, kwargs)
    _extract_cpk_info(cpk_info, kwargs)
    _extract_cpk_scope_info(cpk_scope_info, kwargs)
    _extract_modified_access_conditions(modified_access_conditions, kwargs)
    _extract_source_modified_access_conditions(source_modified_access_conditions, kwargs)
    _extract_source_cpk_info(source_cpk_info, kwargs)
    _extract_sequence_number_access_conditions(sequence_number_access_conditions, kwargs)
    _extract_append_position_access_conditions(append_position_access_conditions, kwargs)
    _extract_container_cpk_scope_info(container_cpk_scope_info, kwargs)
    _extract_blob_modified_access_conditions(blob_modified_access_conditions, kwargs)


# Import the generated mixin classes
from ._operations import _ServiceClientOperationsMixin as _ServiceClientOperationsMixinGenerated
from ._operations import _ContainerClientOperationsMixin as _ContainerClientOperationsMixinGenerated
from ._operations import _BlobClientOperationsMixin as _BlobClientOperationsMixinGenerated
from ._operations import _PageBlobClientOperationsMixin as _PageBlobClientOperationsMixinGenerated
from ._operations import _AppendBlobClientOperationsMixin as _AppendBlobClientOperationsMixinGenerated
from ._operations import _BlockBlobClientOperationsMixin as _BlockBlobClientOperationsMixinGenerated


class _ParameterGroupExtractionMixin:
    """Mixin that intercepts method calls to extract parameter groups from kwargs."""

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)
        # Only wrap public methods (not private/magic and must be callable)
        if not name.startswith("_") and callable(attr):

            def wrapper(*args, **kwargs):
                extract_parameter_groups(kwargs)
                return attr(*args, **kwargs)

            return wrapper
        return attr


class _ServiceClientOperationsMixin(_ParameterGroupExtractionMixin, _ServiceClientOperationsMixinGenerated):
    """Wrapper for ServiceClient operations with parameter group support."""

    pass


class _ContainerClientOperationsMixin(_ParameterGroupExtractionMixin, _ContainerClientOperationsMixinGenerated):
    """Wrapper for ContainerClient operations with parameter group support."""

    pass


class _BlobClientOperationsMixin(_ParameterGroupExtractionMixin, _BlobClientOperationsMixinGenerated):
    """Wrapper for BlobClient operations with parameter group support."""

    pass


class _PageBlobClientOperationsMixin(_ParameterGroupExtractionMixin, _PageBlobClientOperationsMixinGenerated):
    """Wrapper for PageBlobClient operations with parameter group support."""

    pass


class _AppendBlobClientOperationsMixin(_ParameterGroupExtractionMixin, _AppendBlobClientOperationsMixinGenerated):
    """Wrapper for AppendBlobClient operations with parameter group support."""

    pass


class _BlockBlobClientOperationsMixin(_ParameterGroupExtractionMixin, _BlockBlobClientOperationsMixinGenerated):
    """Wrapper for BlockBlobClient operations with parameter group support."""

    pass


__all__: list[str] = [
    "_ServiceClientOperationsMixin",
    "_ContainerClientOperationsMixin",
    "_BlobClientOperationsMixin",
    "_PageBlobClientOperationsMixin",
    "_AppendBlobClientOperationsMixin",
    "_BlockBlobClientOperationsMixin",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
