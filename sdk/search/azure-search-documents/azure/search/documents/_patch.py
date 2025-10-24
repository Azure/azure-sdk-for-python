# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta
from ._client import SearchClient as _SearchClient


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    V2020_06_30 = "2020-06-30"
    V2023_11_01 = "2023-11-01"
    V2024_07_01 = "2024-07-01"
    V2025_08_01_PREVIEW = "2025-08-01-preview"


DEFAULT_VERSION = ApiVersion.V2025_08_01_PREVIEW


class SearchClient(_SearchClient):
    """SearchClient customizations go here."""

    def __init__(self, endpoint, index_name, credential, **kwargs):
        super().__init__(endpoint, credential, index_name, **kwargs)


__all__: list[str] = [
    "SearchClient",
    "ApiVersion",
    "DEFAULT_VERSION",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
