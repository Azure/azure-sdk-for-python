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
        for attr in (
            "cache_control",
            "content_encoding",
            "content_language",
            "content_disposition",
            "content_type",
            "content_md5",
            "transactional_content_hash",
        ):
            value = getattr(path_http_headers, attr, None)
            if value is not None:
                kwargs.setdefault(attr, value)

    modified_access_conditions = kwargs.pop("modified_access_conditions", None)
    if modified_access_conditions is not None:
        for attr in ("if_modified_since", "if_unmodified_since"):
            value = getattr(modified_access_conditions, attr, None)
            if value is not None:
                kwargs.setdefault(attr, value)
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
        lease_id = getattr(lease_access_conditions, "lease_id", None)
        if lease_id is not None:
            kwargs.setdefault("lease_id", lease_id)

    cpk_info = kwargs.pop("cpk_info", None)
    if cpk_info is not None:
        for attr in ("encryption_key", "encryption_key_sha256", "encryption_algorithm"):
            value = getattr(cpk_info, attr, None)
            if value is not None:
                kwargs.setdefault(attr, value)

    source_modified_access_conditions = kwargs.pop("source_modified_access_conditions", None)
    if source_modified_access_conditions is not None:
        for attr in (
            "source_if_match",
            "source_if_none_match",
            "source_if_modified_since",
            "source_if_unmodified_since",
        ):
            value = getattr(source_modified_access_conditions, attr, None)
            if value is not None:
                kwargs.setdefault(attr, value)


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
