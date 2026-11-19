# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from .._utils.model_base import Model, rest_field
from . import _models

__all__: list[str] = []  # Add all objects you want publicly available to users at this package level


def _copy_model(self: Model) -> Model:
    return self.__class__(self._data.copy())  # pylint: disable=protected-access


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    Model.copy = _copy_model

    _models.ImportUpdateRequest.enable_scan = rest_field(
        name="enableScan",
        visibility=["read", "create", "update", "delete", "query"],
        default=False,
    )
    # Recalculate the model metadata so the patched field default is applied.
    Model._calculated.discard(  # pylint: disable=protected-access
        f"{_models.ImportUpdateRequest.__module__}.{_models.ImportUpdateRequest.__qualname__}"
    )
