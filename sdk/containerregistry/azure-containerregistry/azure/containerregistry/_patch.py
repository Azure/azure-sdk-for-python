# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from ._container_registry_client import ContainerRegistryClient
from ._download_stream import DownloadBlobStream
from ._models import (
    ArtifactArchitecture,
    ArtifactOperatingSystem,
    ArtifactManifestProperties,
    RepositoryProperties,
    ArtifactTagProperties,
    GetManifestResult,
    DigestValidationError,
)
from .models import ArtifactManifestOrder, ArtifactTagOrder

__all__: list[str] = [
    "ContainerRegistryClient",
    "ArtifactArchitecture",
    "ArtifactOperatingSystem",
    "ArtifactManifestProperties",
    "RepositoryProperties",
    "ArtifactTagProperties",
    "GetManifestResult",
    "DigestValidationError",
    "DownloadBlobStream",
    "ArtifactManifestOrder",
    "ArtifactTagOrder",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
