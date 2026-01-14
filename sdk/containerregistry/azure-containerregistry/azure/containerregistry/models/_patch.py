# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from ._enums import ArtifactManifestOrder, ArtifactTagOrder

ArtifactManifestOrder.__doc__ = ":no-index:\n\n" + (ArtifactManifestOrder.__doc__ or "")
ArtifactTagOrder.__doc__ = ":no-index:\n\n" + (ArtifactTagOrder.__doc__ or "")

__all__: list[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
