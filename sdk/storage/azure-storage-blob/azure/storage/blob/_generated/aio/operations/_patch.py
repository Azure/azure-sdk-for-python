# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import asyncio
from typing import Any

from ...operations._patch import extract_parameter_groups, _CONTAINER_STRIP_KWARGS

from ._operations import ServiceOperations as _ServiceOpsGen
from ._operations import ContainerOperations as _ContainerOpsGen
from ._operations import BlobOperations as _BlobOpsGen
from ._operations import PageBlobOperations as _PageBlobOpsGen
from ._operations import AppendBlobOperations as _AppendBlobOpsGen
from ._operations import BlockBlobOperations as _BlockBlobOpsGen


class _ParameterGroupExtractionMixin:
    """Intercepts public method calls to extract parameter groups from kwargs."""

    _strip_after_extraction: tuple[str, ...] = ()

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)
        if not name.startswith("_") and callable(attr):
            strip_keys = object.__getattribute__(self, "_strip_after_extraction")
            if asyncio.iscoroutinefunction(attr):

                async def async_wrapper(*args, **kwargs):
                    extract_parameter_groups(kwargs)
                    for k in strip_keys:
                        kwargs.pop(k, None)
                    return await attr(*args, **kwargs)

                return async_wrapper
            else:

                def wrapper(*args, **kwargs):
                    extract_parameter_groups(kwargs)
                    for k in strip_keys:
                        kwargs.pop(k, None)
                    return attr(*args, **kwargs)

                return wrapper
        return attr


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
