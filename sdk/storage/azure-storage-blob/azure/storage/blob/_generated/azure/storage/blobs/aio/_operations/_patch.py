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

# Import the extract_parameter_groups function from the sync _patch module
from ..._operations._patch import extract_parameter_groups


# Import the generated mixin classes
from ._operations import _ServiceClientOperationsMixin as _ServiceClientOperationsMixinGenerated
from ._operations import _ContainerClientOperationsMixin as _ContainerClientOperationsMixinGenerated
from ._operations import _BlobClientOperationsMixin as _BlobClientOperationsMixinGenerated
from ._operations import _PageBlobClientOperationsMixin as _PageBlobClientOperationsMixinGenerated
from ._operations import _AppendBlobClientOperationsMixin as _AppendBlobClientOperationsMixinGenerated
from ._operations import _BlockBlobClientOperationsMixin as _BlockBlobClientOperationsMixinGenerated


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


class _ServiceClientOperationsMixin(_ParameterGroupExtractionMixin, _ServiceClientOperationsMixinGenerated):
    """Wrapper for ServiceClient operations with parameter group support."""

    pass


class _ContainerClientOperationsMixin(_ParameterGroupExtractionMixin, _ContainerClientOperationsMixinGenerated):
    """Wrapper for ContainerClient operations with parameter group support."""

    pass


class _BlobClientOperationsMixin(_ParameterGroupExtractionMixin, _BlobClientOperationsMixinGenerated):
    """Wrapper for BlobClient operations with parameter group support."""

    pass


class _PageBlobClientOperationsMixin(_ParameterGroupExtractionMixin, _PageBlobClientOperationsMixinGenerated):
    """Wrapper for PageBlobClient operations with parameter group support."""

    pass


class _AppendBlobClientOperationsMixin(_ParameterGroupExtractionMixin, _AppendBlobClientOperationsMixinGenerated):
    """Wrapper for AppendBlobClient operations with parameter group support."""

    pass


class _BlockBlobClientOperationsMixin(_ParameterGroupExtractionMixin, _BlockBlobClientOperationsMixinGenerated):
    """Wrapper for BlockBlobClient operations with parameter group support."""

    pass


__all__: list[str] = [
    "_ServiceClientOperationsMixin",
    "_ContainerClientOperationsMixin",
    "_BlobClientOperationsMixin",
    "_PageBlobClientOperationsMixin",
    "_AppendBlobClientOperationsMixin",
    "_BlockBlobClientOperationsMixin",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
