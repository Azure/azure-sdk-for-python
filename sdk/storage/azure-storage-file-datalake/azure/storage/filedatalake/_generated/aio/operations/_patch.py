# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any

from ...operations._patch import extract_parameter_groups
from ._operations import PathOperations as _PathOperations


class _ParameterGroupExtractionMixin:
    """Mixin that extracts parameter group objects into flat kwargs before calling generated operations."""

    async def create(self, **kwargs: Any) -> None:
        extract_parameter_groups(kwargs)
        return await super().create(**kwargs)  # type: ignore[misc]

    async def update(self, **kwargs: Any):
        extract_parameter_groups(kwargs)
        return await super().update(**kwargs)  # type: ignore[misc]

    async def delete(self, **kwargs: Any) -> None:
        extract_parameter_groups(kwargs)
        return await super().delete(**kwargs)  # type: ignore[misc]

    async def set_access_control(self, **kwargs: Any) -> None:
        extract_parameter_groups(kwargs)
        return await super().set_access_control(**kwargs)  # type: ignore[misc]

    async def get_properties(self, **kwargs: Any):
        extract_parameter_groups(kwargs)
        return await super().get_properties(**kwargs)  # type: ignore[misc]

    async def flush_data(self, **kwargs: Any) -> None:
        extract_parameter_groups(kwargs)
        return await super().flush_data(**kwargs)  # type: ignore[misc]

    async def append_data(self, **kwargs: Any) -> None:
        extract_parameter_groups(kwargs)
        return await super().append_data(**kwargs)  # type: ignore[misc]

    async def set_access_control_recursive(self, **kwargs: Any):
        extract_parameter_groups(kwargs)
        return await super().set_access_control_recursive(**kwargs)  # type: ignore[misc]

    async def undelete(self, **kwargs: Any):
        extract_parameter_groups(kwargs)
        return await super().undelete(**kwargs)  # type: ignore[misc]


class PathOperations(_ParameterGroupExtractionMixin, _PathOperations):
    """PathOperations with parameter group extraction support."""


__all__: list[str] = ["PathOperations"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
