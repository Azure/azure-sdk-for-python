# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any

from azure.core import MatchConditions

from ._operations import PathOperations as _PathOperations


def extract_parameter_groups(kwargs: dict) -> None:
    """Extract parameter group objects into flat kwargs for TypeSpec-generated operations.

    The convenience layer passes parameter group model objects (e.g. PathHTTPHeaders,
    ModifiedAccessConditions) but the TypeSpec-generated operations expect flat parameters.
    This function extracts the fields from any parameter group objects found in kwargs.
    """
    path_http_headers = kwargs.pop("path_http_headers", None)
    if path_http_headers is not None:
        kwargs.setdefault("cache_control", getattr(path_http_headers, "cache_control", None))
        kwargs.setdefault("content_encoding", getattr(path_http_headers, "content_encoding", None))
        kwargs.setdefault("content_language", getattr(path_http_headers, "content_language", None))
        kwargs.setdefault("content_disposition", getattr(path_http_headers, "content_disposition", None))
        kwargs.setdefault("content_type", getattr(path_http_headers, "content_type", None))
        kwargs.setdefault("content_md5", getattr(path_http_headers, "content_md5", None))
        kwargs.setdefault("transactional_content_hash", getattr(path_http_headers, "transactional_content_hash", None))

    modified_access_conditions = kwargs.pop("modified_access_conditions", None)
    if modified_access_conditions is not None:
        kwargs.setdefault("if_modified_since", getattr(modified_access_conditions, "if_modified_since", None))
        kwargs.setdefault("if_unmodified_since", getattr(modified_access_conditions, "if_unmodified_since", None))
        if_match = getattr(modified_access_conditions, "if_match", None)
        if_none_match = getattr(modified_access_conditions, "if_none_match", None)
        if if_match:
            kwargs.setdefault("etag", if_match)
            kwargs.setdefault("match_condition", MatchConditions.IfNotModified)
        elif if_none_match == "*":
            kwargs.setdefault("match_condition", MatchConditions.IfMissing)
        elif if_none_match:
            kwargs.setdefault("etag", if_none_match)
            kwargs.setdefault("match_condition", MatchConditions.IfModified)

    lease_access_conditions = kwargs.pop("lease_access_conditions", None)
    if lease_access_conditions is not None:
        kwargs.setdefault("lease_id", getattr(lease_access_conditions, "lease_id", None))

    cpk_info = kwargs.pop("cpk_info", None)
    if cpk_info is not None:
        kwargs.setdefault("encryption_key", getattr(cpk_info, "encryption_key", None))
        kwargs.setdefault("encryption_key_sha256", getattr(cpk_info, "encryption_key_sha256", None))
        kwargs.setdefault("encryption_algorithm", getattr(cpk_info, "encryption_algorithm", None))

    source_modified_access_conditions = kwargs.pop("source_modified_access_conditions", None)
    if source_modified_access_conditions is not None:
        kwargs.setdefault("source_if_match", getattr(source_modified_access_conditions, "source_if_match", None))
        kwargs.setdefault("source_if_none_match", getattr(source_modified_access_conditions, "source_if_none_match", None))
        kwargs.setdefault("source_if_modified_since", getattr(source_modified_access_conditions, "source_if_modified_since", None))
        kwargs.setdefault("source_if_unmodified_since", getattr(source_modified_access_conditions, "source_if_unmodified_since", None))


class _ParameterGroupExtractionMixin:
    """Mixin that extracts parameter group objects into flat kwargs before calling generated operations."""

    def create(self, **kwargs: Any) -> None:
        extract_parameter_groups(kwargs)
        return super().create(**kwargs)  # type: ignore[misc]

    def update(self, **kwargs: Any):
        extract_parameter_groups(kwargs)
        return super().update(**kwargs)  # type: ignore[misc]

    def delete(self, **kwargs: Any) -> None:
        extract_parameter_groups(kwargs)
        return super().delete(**kwargs)  # type: ignore[misc]

    def set_access_control(self, **kwargs: Any) -> None:
        extract_parameter_groups(kwargs)
        return super().set_access_control(**kwargs)  # type: ignore[misc]

    def get_properties(self, **kwargs: Any):
        extract_parameter_groups(kwargs)
        return super().get_properties(**kwargs)  # type: ignore[misc]

    def flush_data(self, **kwargs: Any) -> None:
        extract_parameter_groups(kwargs)
        return super().flush_data(**kwargs)  # type: ignore[misc]

    def append_data(self, **kwargs: Any) -> None:
        extract_parameter_groups(kwargs)
        return super().append_data(**kwargs)  # type: ignore[misc]

    def set_access_control_recursive(self, **kwargs: Any):
        extract_parameter_groups(kwargs)
        return super().set_access_control_recursive(**kwargs)  # type: ignore[misc]

    def undelete(self, **kwargs: Any):
        extract_parameter_groups(kwargs)
        return super().undelete(**kwargs)  # type: ignore[misc]


class PathOperations(_ParameterGroupExtractionMixin, _PathOperations):
    """PathOperations with parameter group extraction support."""


__all__: list[str] = ["PathOperations"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
