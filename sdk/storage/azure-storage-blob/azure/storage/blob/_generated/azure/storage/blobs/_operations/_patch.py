# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Mapping, Optional

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


def _extract_blob_http_headers(
    blob_http_headers: Optional[BlobHTTPHeaders],
    kwargs: dict[str, Any],
) -> None:
    """Extract BlobHTTPHeaders fields into kwargs if not already set."""
    if blob_http_headers is not None:
        if kwargs.get("blob_cache_control") is None:
            kwargs["blob_cache_control"] = blob_http_headers.get("blob_cache_control")
        if kwargs.get("blob_content_type") is None:
            kwargs["blob_content_type"] = blob_http_headers.get("blob_content_type")
        if kwargs.get("blob_content_md5") is None:
            kwargs["blob_content_md5"] = blob_http_headers.get("blob_content_md5")
        if kwargs.get("blob_content_encoding") is None:
            kwargs["blob_content_encoding"] = blob_http_headers.get("blob_content_encoding")
        if kwargs.get("blob_content_language") is None:
            kwargs["blob_content_language"] = blob_http_headers.get("blob_content_language")
        if kwargs.get("blob_content_disposition") is None:
            kwargs["blob_content_disposition"] = blob_http_headers.get("blob_content_disposition")


def _extract_lease_access_conditions(
    lease_access_conditions: Optional[LeaseAccessConditions],
    kwargs: dict[str, Any],
) -> None:
    """Extract LeaseAccessConditions fields into kwargs if not already set."""
    if lease_access_conditions is not None:
        if kwargs.get("lease_id") is None:
            kwargs["lease_id"] = lease_access_conditions.get("lease_id")


def _extract_cpk_info(
    cpk_info: Optional[CpkInfo],
    kwargs: dict[str, Any],
) -> None:
    """Extract CpkInfo fields into kwargs if not already set."""
    if cpk_info is not None:
        if kwargs.get("encryption_key") is None:
            kwargs["encryption_key"] = cpk_info.get("encryption_key")
        if kwargs.get("encryption_key_sha256") is None:
            kwargs["encryption_key_sha256"] = cpk_info.get("encryption_key_sha256")
        if kwargs.get("encryption_algorithm") is None:
            kwargs["encryption_algorithm"] = cpk_info.get("encryption_algorithm")


def _extract_cpk_scope_info(
    cpk_scope_info: Optional[CpkScopeInfo],
    kwargs: dict[str, Any],
) -> None:
    """Extract CpkScopeInfo fields into kwargs if not already set."""
    if cpk_scope_info is not None:
        if kwargs.get("encryption_scope") is None:
            kwargs["encryption_scope"] = cpk_scope_info.get("encryption_scope")


def _extract_modified_access_conditions(
    modified_access_conditions: Optional[ModifiedAccessConditions],
    kwargs: dict[str, Any],
) -> None:
    """Extract ModifiedAccessConditions fields into kwargs if not already set."""
    if modified_access_conditions is not None:
        if kwargs.get("if_modified_since") is None:
            kwargs["if_modified_since"] = modified_access_conditions.get("if_modified_since")
        if kwargs.get("if_unmodified_since") is None:
            kwargs["if_unmodified_since"] = modified_access_conditions.get("if_unmodified_since")
        if kwargs.get("etag") is None:
            kwargs["etag"] = modified_access_conditions.get("etag")
        if kwargs.get("match_condition") is None:
            kwargs["match_condition"] = modified_access_conditions.get("match_condition")
        if kwargs.get("if_tags") is None:
            kwargs["if_tags"] = modified_access_conditions.get("if_tags")


def _extract_source_modified_access_conditions(
    source_modified_access_conditions: Optional[SourceModifiedAccessConditions],
    kwargs: dict[str, Any],
) -> None:
    """Extract SourceModifiedAccessConditions fields into kwargs if not already set."""
    if source_modified_access_conditions is not None:
        if kwargs.get("source_if_modified_since") is None:
            kwargs["source_if_modified_since"] = source_modified_access_conditions.get("source_if_modified_since")
        if kwargs.get("source_if_unmodified_since") is None:
            kwargs["source_if_unmodified_since"] = source_modified_access_conditions.get("source_if_unmodified_since")
        if kwargs.get("source_if_match") is None:
            kwargs["source_if_match"] = source_modified_access_conditions.get("source_if_match")
        if kwargs.get("source_if_none_match") is None:
            kwargs["source_if_none_match"] = source_modified_access_conditions.get("source_if_none_match")
        if kwargs.get("source_if_tags") is None:
            kwargs["source_if_tags"] = source_modified_access_conditions.get("source_if_tags")


def _extract_source_cpk_info(
    source_cpk_info: Optional[SourceCpkInfo],
    kwargs: dict[str, Any],
) -> None:
    """Extract SourceCpkInfo fields into kwargs if not already set."""
    if source_cpk_info is not None:
        if kwargs.get("source_encryption_key") is None:
            kwargs["source_encryption_key"] = source_cpk_info.get("source_encryption_key")
        if kwargs.get("source_encryption_key_sha256") is None:
            kwargs["source_encryption_key_sha256"] = source_cpk_info.get("source_encryption_key_sha256")
        if kwargs.get("source_encryption_algorithm") is None:
            kwargs["source_encryption_algorithm"] = source_cpk_info.get("source_encryption_algorithm")


def _extract_sequence_number_access_conditions(
    sequence_number_access_conditions: Optional[SequenceNumberAccessConditions],
    kwargs: dict[str, Any],
) -> None:
    """Extract SequenceNumberAccessConditions fields into kwargs if not already set."""
    if sequence_number_access_conditions is not None:
        if kwargs.get("if_sequence_number_less_than_or_equal_to") is None:
            kwargs["if_sequence_number_less_than_or_equal_to"] = sequence_number_access_conditions.get(
                "if_sequence_number_less_than_or_equal_to"
            )
        if kwargs.get("if_sequence_number_less_than") is None:
            kwargs["if_sequence_number_less_than"] = sequence_number_access_conditions.get(
                "if_sequence_number_less_than"
            )
        if kwargs.get("if_sequence_number_equal_to") is None:
            kwargs["if_sequence_number_equal_to"] = sequence_number_access_conditions.get("if_sequence_number_equal_to")


def _extract_append_position_access_conditions(
    append_position_access_conditions: Optional[AppendPositionAccessConditions],
    kwargs: dict[str, Any],
) -> None:
    """Extract AppendPositionAccessConditions fields into kwargs if not already set."""
    if append_position_access_conditions is not None:
        if kwargs.get("max_size") is None:
            kwargs["max_size"] = append_position_access_conditions.get("max_size")
        if kwargs.get("append_position") is None:
            kwargs["append_position"] = append_position_access_conditions.get("append_position")


def _extract_container_cpk_scope_info(
    container_cpk_scope_info: Optional[ContainerCpkScopeInfo],
    kwargs: dict[str, Any],
) -> None:
    """Extract ContainerCpkScopeInfo fields into kwargs if not already set."""
    if container_cpk_scope_info is not None:
        if kwargs.get("default_encryption_scope") is None:
            kwargs["default_encryption_scope"] = container_cpk_scope_info.get("default_encryption_scope")
        if kwargs.get("prevent_encryption_scope_override") is None:
            kwargs["prevent_encryption_scope_override"] = container_cpk_scope_info.get(
                "prevent_encryption_scope_override"
            )


def _extract_blob_modified_access_conditions(
    blob_modified_access_conditions: Optional[BlobModifiedAccessConditions],
    kwargs: dict[str, Any],
) -> None:
    """Extract BlobModifiedAccessConditions fields into kwargs if not already set."""
    if blob_modified_access_conditions is not None:
        if kwargs.get("if_modified_since") is None:
            kwargs["if_modified_since"] = blob_modified_access_conditions.get("if_modified_since")
        if kwargs.get("if_unmodified_since") is None:
            kwargs["if_unmodified_since"] = blob_modified_access_conditions.get("if_unmodified_since")
        if kwargs.get("etag") is None:
            kwargs["etag"] = blob_modified_access_conditions.get("etag")
        if kwargs.get("match_condition") is None:
            kwargs["match_condition"] = blob_modified_access_conditions.get("match_condition")


def extract_parameter_groups(kwargs: dict[str, Any]) -> None:
    """
    Extract all parameter group objects from kwargs and flatten their fields.

    This function supports backward compatibility with the old API that accepted
    parameter group objects like BlobHTTPHeaders, LeaseAccessConditions, etc.
    """
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


__all__: list[str] = [
    "_ServiceClientOperationsMixin",
    "_ContainerClientOperationsMixin",
    "_BlobClientOperationsMixin",
    "_PageBlobClientOperationsMixin",
    "_AppendBlobClientOperationsMixin",
    "_BlockBlobClientOperationsMixin",
]


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


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
