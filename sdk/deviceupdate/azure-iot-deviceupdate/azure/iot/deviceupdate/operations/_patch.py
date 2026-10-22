# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, List, Optional

from azure.core import MatchConditions

from ._operations import (
    DeviceManagementOperations as DeviceManagementOperationsGenerated,
    DeviceUpdateOperations as DeviceUpdateOperationsGenerated,
)


def _apply_if_none_match(kwargs: Any, if_none_match: Optional[str]) -> None:
    """Restore the 1.0.0 ``if_none_match`` behavior by sending the raw
    ``If-None-Match`` header value as-is (the generated client instead exposes the
    ``etag`` / ``match_condition`` pattern).

    :param kwargs: The keyword arguments forwarded to the generated operation.
    :type kwargs: any
    :param if_none_match: The raw ``If-None-Match`` header value, or ``None``.
    :type if_none_match: str or None
    """
    if if_none_match is not None:
        headers = kwargs.setdefault("headers", {})
        headers.setdefault("If-None-Match", if_none_match)


class DeviceUpdateOperations(DeviceUpdateOperationsGenerated):
    def get_update(
        self,
        provider: str,
        name: str,
        version: str,
        *,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_none_match: Optional[str] = None,
        **kwargs: Any,
    ):
        _apply_if_none_match(kwargs, if_none_match)
        return super().get_update(provider, name, version, etag=etag, match_condition=match_condition, **kwargs)

    def get_file(
        self,
        provider: str,
        name: str,
        version: str,
        file_id: str,
        *,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_none_match: Optional[str] = None,
        **kwargs: Any,
    ):
        _apply_if_none_match(kwargs, if_none_match)
        return super().get_file(provider, name, version, file_id, etag=etag, match_condition=match_condition, **kwargs)

    def get_operation_status(
        self,
        operation_id: str,
        *,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_none_match: Optional[str] = None,
        **kwargs: Any,
    ):
        _apply_if_none_match(kwargs, if_none_match)
        return super().get_operation_status(operation_id, etag=etag, match_condition=match_condition, **kwargs)


class DeviceManagementOperations(DeviceManagementOperationsGenerated):
    def get_operation_status(
        self,
        operation_id: str,
        *,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        if_none_match: Optional[str] = None,
        **kwargs: Any,
    ):
        _apply_if_none_match(kwargs, if_none_match)
        return super().get_operation_status(operation_id, etag=etag, match_condition=match_condition, **kwargs)


__all__: List[str] = [
    "DeviceUpdateOperations",
    "DeviceManagementOperations",
]  # Add all objects you want publicly available at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
