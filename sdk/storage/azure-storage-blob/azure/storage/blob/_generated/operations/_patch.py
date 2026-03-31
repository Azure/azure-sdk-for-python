# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional

from azure.core import MatchConditions

from .._utils import utils as _generated_utils

# Override quote_etag to be a no-op — the old storage SDK never wrapped
# etags in double quotes and existing recordings expect unquoted values.
_generated_utils.quote_etag = lambda etag: etag

# Parameter group extraction helpers


def _flatten_group(group: object, fields: list[str], kwargs: dict[str, Any]) -> None:
    """Copy each *field* from *group* into *kwargs* (if non-None and not already set)."""
    for field in fields:
        value = getattr(group, field, None)
        if value is not None:
            kwargs.setdefault(field, value)


def _convert_to_etag_match_condition(
    if_match: Optional[str],
    if_none_match: Optional[str],
    kwargs: dict[str, Any],
) -> None:
    """Translate old-style if_match/if_none_match into etag + match_condition.

    The new generated code uses ``etag`` / ``match_condition`` (from
    ``azure.core.MatchConditions``) which are converted internally via
    ``prep_if_match`` / ``prep_if_none_match``.
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


# (kwarg_name, fields_to_flatten, needs_etag_conversion)
_PARAMETER_GROUPS: list[tuple[str, list[str], bool]] = [
    (
        "blob_http_headers",
        [
            "blob_cache_control",
            "blob_content_type",
            "blob_content_md5",
            "blob_content_encoding",
            "blob_content_language",
            "blob_content_disposition",
        ],
        False,
    ),
    ("lease_access_conditions", ["lease_id"], False),
    ("cpk_info", ["encryption_key", "encryption_key_sha256", "encryption_algorithm"], False),
    ("cpk_scope_info", ["encryption_scope"], False),
    (
        "source_cpk_info",
        [
            "source_encryption_key",
            "source_encryption_key_sha256",
            "source_encryption_algorithm",
        ],
        False,
    ),
    (
        "sequence_number_access_conditions",
        [
            "if_sequence_number_less_than_or_equal_to",
            "if_sequence_number_less_than",
            "if_sequence_number_equal_to",
        ],
        False,
    ),
    ("append_position_access_conditions", ["max_size", "append_position"], False),
    (
        "container_cpk_scope_info",
        [
            "default_encryption_scope",
            "prevent_encryption_scope_override",
        ],
        False,
    ),
    # ModifiedAccessConditions needs etag/match_condition conversion
    (
        "modified_access_conditions",
        [
            "if_modified_since",
            "if_unmodified_since",
            "if_tags",
        ],
        True,
    ),
    # SourceModifiedAccessConditions — fields pass through directly
    (
        "source_modified_access_conditions",
        [
            "source_if_modified_since",
            "source_if_unmodified_since",
            "source_if_tags",
            "source_if_match",
            "source_if_none_match",
        ],
        False,
    ),
    # BlobModifiedAccessConditions — if_match/if_none_match pass through
    # directly (they map to x-ms-blob-if-match, not standard If-Match)
    (
        "blob_modified_access_conditions",
        [
            "if_modified_since",
            "if_unmodified_since",
            "if_match",
            "if_none_match",
        ],
        False,
    ),
]


def extract_parameter_groups(kwargs: dict[str, Any]) -> None:
    """Pop all parameter-group objects from *kwargs* and flatten their fields."""

    for kwarg_name, fields, needs_etag in _PARAMETER_GROUPS:
        group = kwargs.pop(kwarg_name, None)
        if group is not None:
            _flatten_group(group, fields, kwargs)
            if needs_etag:
                _convert_to_etag_match_condition(
                    getattr(group, "if_match", None),
                    getattr(group, "if_none_match", None),
                    kwargs,
                )


# ---------------------------------------------------------------------------
# Operation class wrappers
# ---------------------------------------------------------------------------

from ._operations import ServiceOperations as _ServiceOpsGen  # noqa: E402
from ._operations import ContainerOperations as _ContainerOpsGen  # noqa: E402
from ._operations import BlobOperations as _BlobOpsGen  # noqa: E402
from ._operations import PageBlobOperations as _PageBlobOpsGen  # noqa: E402
from ._operations import AppendBlobOperations as _AppendBlobOpsGen  # noqa: E402
from ._operations import BlockBlobOperations as _BlockBlobOpsGen  # noqa: E402


class _ParameterGroupExtractionMixin:
    """Intercepts public method calls to extract parameter groups from kwargs."""

    # Subclasses override to strip kwargs unsupported by the target operation
    # (e.g. container ops don't accept etag/match_condition/if_tags).
    _strip_after_extraction: tuple[str, ...] = ()

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)
        if not name.startswith("_") and callable(attr):
            strip_keys = object.__getattribute__(self, "_strip_after_extraction")

            def wrapper(*args, **kwargs):
                extract_parameter_groups(kwargs)
                for k in strip_keys:
                    kwargs.pop(k, None)
                return attr(*args, **kwargs)

            return wrapper
        return attr


# Container/Service REST APIs don't support If-Match/If-None-Match/x-ms-if-tags,
# so strip these after extraction to prevent them leaking to the transport.
_CONTAINER_STRIP_KWARGS = ("match_condition", "etag", "if_tags")


class ServiceOperations(_ParameterGroupExtractionMixin, _ServiceOpsGen):
    _strip_after_extraction = _CONTAINER_STRIP_KWARGS


class ContainerOperations(_ParameterGroupExtractionMixin, _ContainerOpsGen):
    _strip_after_extraction = _CONTAINER_STRIP_KWARGS


class BlobOperations(_ParameterGroupExtractionMixin, _BlobOpsGen):
    pass


class PageBlobOperations(_ParameterGroupExtractionMixin, _PageBlobOpsGen):
    pass


class AppendBlobOperations(_ParameterGroupExtractionMixin, _AppendBlobOpsGen):
    pass


class BlockBlobOperations(_ParameterGroupExtractionMixin, _BlockBlobOpsGen):
    pass


__all__: list[str] = [
    "ServiceOperations",
    "ContainerOperations",
    "BlobOperations",
    "PageBlobOperations",
    "AppendBlobOperations",
    "BlockBlobOperations",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
