# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Optional
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class AppendPositionAccessConditions:
    """Parameter group for append position access conditions."""

    def __init__(
        self,
        *,
        max_size: Optional[int] = None,
        append_position: Optional[int] = None,
    ):
        self.max_size = max_size
        self.append_position = append_position


class BlobHTTPHeaders:
    """Parameter group for blob HTTP headers."""

    def __init__(
        self,
        *,
        blob_cache_control: Optional[str] = None,
        blob_content_type: Optional[str] = None,
        blob_content_md5: Optional[bytes] = None,
        blob_content_encoding: Optional[str] = None,
        blob_content_language: Optional[str] = None,
        blob_content_disposition: Optional[str] = None,
    ):
        self.blob_cache_control = blob_cache_control
        self.blob_content_type = blob_content_type
        self.blob_content_md5 = blob_content_md5
        self.blob_content_encoding = blob_content_encoding
        self.blob_content_language = blob_content_language
        self.blob_content_disposition = blob_content_disposition


class BlobModifiedAccessConditions:
    """Parameter group for blob modified access conditions."""

    def __init__(
        self,
        *,
        if_modified_since: Optional[str] = None,
        if_unmodified_since: Optional[str] = None,
        if_match: Optional[str] = None,
        if_none_match: Optional[str] = None,
    ):
        self.if_modified_since = if_modified_since
        self.if_unmodified_since = if_unmodified_since
        self.if_match = if_match
        self.if_none_match = if_none_match


class ContainerCpkScopeInfo:
    """Parameter group for container CPK scope info."""

    def __init__(
        self,
        *,
        default_encryption_scope: Optional[str] = None,
        prevent_encryption_scope_override: Optional[bool] = None,
    ):
        self.default_encryption_scope = default_encryption_scope
        self.prevent_encryption_scope_override = prevent_encryption_scope_override


class CpkInfo:
    """Parameter group for CPK info."""

    def __init__(
        self,
        *,
        encryption_key: Optional[str] = None,
        encryption_key_sha256: Optional[str] = None,
        encryption_algorithm: Optional[str] = None,
    ):
        self.encryption_key = encryption_key
        self.encryption_key_sha256 = encryption_key_sha256
        self.encryption_algorithm = encryption_algorithm

class ModifiedAccessConditions:
    """Parameter group for modified access conditions."""

    def __init__(
        self,
        *,
        if_modified_since: Optional[str] = None,
        if_unmodified_since: Optional[str] = None,
        if_match: Optional[str] = None,
        if_none_match: Optional[str] = None,
        if_tags: Optional[str] = None,
    ):
        self.if_modified_since = if_modified_since
        self.if_unmodified_since = if_unmodified_since
        self.if_match = if_match
        self.if_none_match = if_none_match
        self.if_tags = if_tags


class QueryFormatType(Enum, metaclass=CaseInsensitiveEnumMeta):
    """The query format type."""

    DELIMITED = "delimited"
    JSON = "json"
    ARROW = "arrow"
    PARQUET = "parquet"


class SequenceNumberAccessConditions:
    """Parameter group for sequence number access conditions."""

    def __init__(
        self,
        *,
        if_sequence_number_less_than_or_equal_to: Optional[int] = None,
        if_sequence_number_less_than: Optional[int] = None,
        if_sequence_number_equal_to: Optional[int] = None,
    ):
        self.if_sequence_number_less_than_or_equal_to = if_sequence_number_less_than_or_equal_to
        self.if_sequence_number_less_than = if_sequence_number_less_than
        self.if_sequence_number_equal_to = if_sequence_number_equal_to


class SourceCpkInfo:
    """Parameter group for source CPK info."""

    def __init__(
        self,
        *,
        source_encryption_key: Optional[str] = None,
        source_encryption_key_sha256: Optional[str] = None,
        source_encryption_algorithm: Optional[str] = None,
    ):
        self.source_encryption_key = source_encryption_key
        self.source_encryption_key_sha256 = source_encryption_key_sha256
        self.source_encryption_algorithm = source_encryption_algorithm


class SourceModifiedAccessConditions:
    """Parameter group for source modified access conditions."""

    def __init__(
        self,
        *,
        source_if_modified_since: Optional[str] = None,
        source_if_unmodified_since: Optional[str] = None,
        source_if_match: Optional[str] = None,
        source_if_none_match: Optional[str] = None,
        source_if_tags: Optional[str] = None,
    ):
        self.source_if_modified_since = source_if_modified_since
        self.source_if_unmodified_since = source_if_unmodified_since
        self.source_if_match = source_if_match
        self.source_if_none_match = source_if_none_match
        self.source_if_tags = source_if_tags


__all__: list[str] = [
    "AppendPositionAccessConditions",
    "BlobHTTPHeaders",
    "BlobModifiedAccessConditions",
    "ContainerCpkScopeInfo",
    "CpkInfo",
    "ModifiedAccessConditions",
    "QueryFormatType",
    "SequenceNumberAccessConditions",
    "SourceCpkInfo",
    "SourceModifiedAccessConditions",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
