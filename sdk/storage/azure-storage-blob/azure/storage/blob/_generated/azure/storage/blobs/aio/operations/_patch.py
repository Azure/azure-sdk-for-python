# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import asyncio
import inspect
from typing import Any

# Import the extract_parameter_groups function from the sync operations patch
from ...operations._patch import extract_parameter_groups


# Import the generated operation classes
from ._operations import ServiceOperations as ServiceOperationsGenerated
from ._operations import ContainerOperations as ContainerOperationsGenerated
from ._operations import BlobOperations as BlobOperationsGenerated
from ._operations import PageBlobOperations as PageBlobOperationsGenerated
from ._operations import AppendBlobOperations as AppendBlobOperationsGenerated
from ._operations import BlockBlobOperations as BlockBlobOperationsGenerated


class _ParameterGroupExtractionMixin:
    """Mixin that intercepts method calls to extract parameter groups from kwargs."""

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)
        # Only wrap public methods (not private/magic and must be callable)
        if not name.startswith("_") and callable(attr):
            if asyncio.iscoroutinefunction(attr):

                async def async_wrapper(*args, **kwargs):
                    extract_parameter_groups(kwargs)
                    return await attr(*args, **kwargs)

                return async_wrapper
            else:

                def wrapper(*args, **kwargs):
                    extract_parameter_groups(kwargs)
                    return attr(*args, **kwargs)

                return wrapper
        return attr


class ServiceOperations(_ParameterGroupExtractionMixin, ServiceOperationsGenerated):
    """Wrapper for ServiceOperations with parameter group support."""

    pass


class ContainerOperations(_ParameterGroupExtractionMixin, ContainerOperationsGenerated):
    """Wrapper for ContainerOperations with parameter group support."""

    pass


class BlobOperations(_ParameterGroupExtractionMixin, BlobOperationsGenerated):
    """Wrapper for BlobOperations with parameter group support."""

    pass


class PageBlobOperations(_ParameterGroupExtractionMixin, PageBlobOperationsGenerated):
    """Wrapper for PageBlobOperations with parameter group support."""

    pass


class AppendBlobOperations(_ParameterGroupExtractionMixin, AppendBlobOperationsGenerated):
    """Wrapper for AppendBlobOperations with parameter group support."""

    pass


class BlockBlobOperations(_ParameterGroupExtractionMixin, BlockBlobOperationsGenerated):
    """Wrapper for BlockBlobOperations with parameter group support."""

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
