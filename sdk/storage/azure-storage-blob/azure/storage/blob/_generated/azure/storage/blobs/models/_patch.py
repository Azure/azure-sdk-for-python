# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Optional
from typing_extensions import TypedDict, NotRequired
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class AppendPositionAccessConditions(TypedDict, total=False):
    """Parameter group for append position access conditions."""

    max_size: NotRequired[Optional[int]]
    append_position: NotRequired[Optional[int]]


class BlobHTTPHeaders(TypedDict, total=False):
    """Parameter group for blob HTTP headers."""

    blob_cache_control: NotRequired[Optional[str]]
    blob_content_type: NotRequired[Optional[str]]
    blob_content_md5: NotRequired[Optional[bytes]]
    blob_content_encoding: NotRequired[Optional[str]]
    blob_content_language: NotRequired[Optional[str]]
    blob_content_disposition: NotRequired[Optional[str]]


class BlobModifiedAccessConditions(TypedDict, total=False):
    """Parameter group for blob modified access conditions."""

    if_modified_since: NotRequired[Optional[str]]
    if_unmodified_since: NotRequired[Optional[str]]
    if_match: NotRequired[Optional[str]]
    if_none_match: NotRequired[Optional[str]]

class ContainerCpkScopeInfo(TypedDict, total=False):
    """Parameter group for container CPK scope info."""

    default_encryption_scope: NotRequired[Optional[str]]
    prevent_encryption_scope_override: NotRequired[Optional[bool]]


class CpkScopeInfo(TypedDict, total=False):
    """Parameter group.

    encryption_scope: Optional. Version 2019-07-07 and later.  Specifies the name of the
     encryption scope to use to encrypt the data provided in the request. If not specified,
     encryption is performed with the default account encryption scope.  For more information, see
     Encryption at Rest for Azure Storage Services.
    """

    encryption_scope: NotRequired[Optional[str]]


class CpkInfo(TypedDict, total=False):
    """Parameter group for CPK info."""

    encryption_key: NotRequired[Optional[str]]
    encryption_key_sha256: NotRequired[Optional[str]]
    encryption_algorithm: NotRequired[Optional[str]]

class ModifiedAccessConditions(TypedDict, total=False):
    """Parameter group for modified access conditions."""

    if_modified_since: NotRequired[Optional[str]]
    if_unmodified_since: NotRequired[Optional[str]]
    if_match: NotRequired[Optional[str]]
    if_none_match: NotRequired[Optional[str]]
    if_tags: NotRequired[Optional[str]]

class SequenceNumberAccessConditions(TypedDict, total=False):
    """Parameter group for sequence number access conditions."""

    if_sequence_number_less_than_or_equal_to: NotRequired[Optional[int]]
    if_sequence_number_less_than: NotRequired[Optional[int]]
    if_sequence_number_equal_to: NotRequired[Optional[int]]


class SourceCpkInfo(TypedDict, total=False):
    """Parameter group for source CPK info."""

    source_encryption_key: NotRequired[Optional[str]]
    source_encryption_key_sha256: NotRequired[Optional[str]]
    source_encryption_algorithm: NotRequired[Optional[str]]

class SourceModifiedAccessConditions(TypedDict, total=False):
    """Parameter group for source modified access conditions."""

    source_if_modified_since: NotRequired[Optional[str]]
    source_if_unmodified_since: NotRequired[Optional[str]]
    source_if_match: NotRequired[Optional[str]]
    source_if_none_match: NotRequired[Optional[str]]
    source_if_tags: NotRequired[Optional[str]]


class LeaseAccessConditions(TypedDict, total=False):
    """Parameter group.

    lease_id: If specified, the operation only succeeds if the resource's lease is active and
    matches this ID.
    """

    lease_id: NotRequired[Optional[str]]


__all__: list[str] = [
    "AppendPositionAccessConditions",
    "BlobHTTPHeaders",
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
