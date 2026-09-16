# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

# Add all objects you want publicly available to users at this package level.
__all__: list[str] = []


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    from .._validation import api_version_validation
    from ._operations import _ContentSafetyClientOperationsMixin

    _ContentSafetyClientOperationsMixin.unified_moderate = api_version_validation(
        method_added_on="2026-09-01-preview",
        api_versions_list=["2026-09-01-preview"],
    )(_ContentSafetyClientOperationsMixin.unified_moderate)
