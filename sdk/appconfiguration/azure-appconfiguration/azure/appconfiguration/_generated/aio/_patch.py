# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List

__all__: List[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    from ._operations._patch import AzureAppConfigurationClientOperationsMixin as _Patched
    from ._operations._operations import _AzureAppConfigurationClientOperationsMixin as _Raw

    for _name, _attr in vars(_Patched).items():
        if _name in ("__dict__", "__weakref__", "__doc__", "__module__", "__qualname__"):
            continue
        setattr(_Raw, _name, _attr)
