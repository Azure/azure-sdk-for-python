# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from .models import(
    ArtifactTagProperties,
    RepositoryWriteableProperties as RepositoryProperties,
    ArtifactManifestProperties,
    ArtifactManifestOrder,
    ArtifactTagOrder,
    ArtifactArchitecture,
    ArtifactOperatingSystem,
)

class DigestValidationError(ValueError):
    """Thrown when a manifest digest validation fails."""

    message: str
    """Message for caller describing the reason for the failure."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)




__all__: list[str] = [
    "ArtifactTagProperties",
    "RepositoryProperties",
    "ArtifactManifestProperties",
    "ArtifactManifestOrder",
    "ArtifactTagOrder",
    "ArtifactArchitecture",
    "ArtifactOperatingSystem",
    "DigestValidationError",
]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
