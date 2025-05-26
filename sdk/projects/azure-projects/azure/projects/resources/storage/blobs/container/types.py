# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import Literal, Dict, Union
from typing_extensions import TypedDict

from ....._bicep.expressions import Parameter


VERSION = "2022-09-01"


class ImmutableStorageWithVersioning(TypedDict, total=False):
    enabled: Union[bool, Parameter]
    """This is an immutable property, when set to true it enables object level immutability at the container level."""


class ContainerProperties(TypedDict, total=False):
    defaultEncryptionScope: Union[str, Parameter]
    """Default the container to use specified encryption scope for all writes."""
    denyEncryptionScopeOverride: Union[bool, Parameter]
    """Block override of encryption scope from the container default."""
    enableNfsV3AllSquash: Union[bool, Parameter]
    """Enable NFSv3 all squash on blob container."""
    enableNfsV3RootSquash: Union[bool, Parameter]
    """Enable NFSv3 root squash on blob container."""
    immutabilityPolicyName: Union[bool, Parameter]
    """Name of the immutable policy."""
    immutableStorageWithVersioning: Union["ImmutableStorageWithVersioning", Parameter]
    """The object level immutability property of the container. The property is immutable and can only be set to true at the container creation time. Existing containers must undergo a migration process."""
    metadata: Dict[str, str]
    """A name-value pair to associate with the container as metadata."""
    publicAccess: Union[Literal["Blob", "Container", "None"], Parameter]
    """Specifies whether data in the container may be accessed publicly and the level of access."""


class ContainerResource(TypedDict, total=False):
    name: Union[str, Parameter]
    """The resource name."""
    properties: ContainerProperties
    """The properties of a container."""
