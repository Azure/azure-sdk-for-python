# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from __future__ import annotations
from typing import Literal, TypedDict, Union, Any

from ....._bicep.expressions import Parameter

VERSION = '2024-01-01'


class ContainerProperties(TypedDict, total=False):
    defaultEncryptionScope: Union[str, Parameter]
    """Default the container to use specified encryption scope for all writes."""
    denyEncryptionScopeOverride: Union[bool, Parameter]
    """Block override of encryption scope from the container default."""
    enableNfsV3AllSquash: Union[bool, Parameter]
    """Enable NFSv3 all squash on blob container."""
    enableNfsV3RootSquash: Union[bool, Parameter]
    """Enable NFSv3 root squash on blob container."""
    immutableStorageWithVersioning: Union[ContainerImmutableStorageWithVersioning, Parameter]
    """The object level immutability property of the container. The property is immutable and can only be set to true at the container creation time. Existing containers must undergo a migration process."""
    metadata: Union[ContainerProperties, Parameter]
    """A name-value pair to associate with the container as metadata."""
    publicAccess: Union[Literal['Blob', 'Container', 'None'], Parameter]
    """Specifies whether data in the container may be accessed publicly and the level of access."""


class ContainerImmutableStorageWithVersioning(TypedDict, total=False):
    enabled: Union[bool, Parameter]
    """This is an immutable property, when set to true it enables object level immutability at the container level."""


class ContainerResource(TypedDict, total=False):
    name: Union[str, Parameter]
    """The resource name"""
    properties: Union[ContainerProperties, Parameter]
    """Properties of the blob container."""
    parent: Any
    """The Symbolic name of the resource that is the parent for this resource."""


