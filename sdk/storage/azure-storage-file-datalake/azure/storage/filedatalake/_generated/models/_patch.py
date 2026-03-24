# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
from typing import Optional

from .._utils.model_base import Model as _Model, rest_field
from ._models import PathItem

_ALL_VISIBILITY = ["read", "create", "update", "delete", "query"]


class CpkInfo(_Model):
    encryption_key: Optional[str] = rest_field(name="encryption_key", visibility=_ALL_VISIBILITY)
    encryption_key_sha256: Optional[str] = rest_field(name="encryption_key_sha256", visibility=_ALL_VISIBILITY)
    encryption_algorithm: Optional[str] = rest_field(name="encryption_algorithm", visibility=_ALL_VISIBILITY)


class LeaseAccessConditions(_Model):
    lease_id: Optional[str] = rest_field(name="lease_id", visibility=_ALL_VISIBILITY)


class ModifiedAccessConditions(_Model):
    if_modified_since: Optional[datetime.datetime] = rest_field(name="if_modified_since", visibility=_ALL_VISIBILITY)
    if_unmodified_since: Optional[datetime.datetime] = rest_field(
        name="if_unmodified_since", visibility=_ALL_VISIBILITY
    )
    if_match: Optional[str] = rest_field(name="if_match", visibility=_ALL_VISIBILITY)
    if_none_match: Optional[str] = rest_field(name="if_none_match", visibility=_ALL_VISIBILITY)


class PathHTTPHeaders(_Model):
    cache_control: Optional[str] = rest_field(name="cache_control", visibility=_ALL_VISIBILITY)
    content_encoding: Optional[str] = rest_field(name="content_encoding", visibility=_ALL_VISIBILITY)
    content_language: Optional[str] = rest_field(name="content_language", visibility=_ALL_VISIBILITY)
    content_disposition: Optional[str] = rest_field(name="content_disposition", visibility=_ALL_VISIBILITY)
    content_type: Optional[str] = rest_field(name="content_type", visibility=_ALL_VISIBILITY)
    content_md5: Optional[bytes] = rest_field(name="content_md5", visibility=_ALL_VISIBILITY)
    transactional_content_hash: Optional[bytes] = rest_field(
        name="transactional_content_hash", visibility=_ALL_VISIBILITY
    )


class SourceModifiedAccessConditions(_Model):
    source_if_match: Optional[str] = rest_field(name="source_if_match", visibility=_ALL_VISIBILITY)
    source_if_none_match: Optional[str] = rest_field(name="source_if_none_match", visibility=_ALL_VISIBILITY)
    source_if_modified_since: Optional[datetime.datetime] = rest_field(
        name="source_if_modified_since", visibility=_ALL_VISIBILITY
    )
    source_if_unmodified_since: Optional[datetime.datetime] = rest_field(
        name="source_if_unmodified_since", visibility=_ALL_VISIBILITY
    )


# Alias: the old generated code exported "Path"; the new code uses "PathItem".
Path = PathItem


__all__: list[str] = [
    "CpkInfo",
    "LeaseAccessConditions",
    "ModifiedAccessConditions",
    "Path",
    "PathHTTPHeaders",
    "SourceModifiedAccessConditions",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
