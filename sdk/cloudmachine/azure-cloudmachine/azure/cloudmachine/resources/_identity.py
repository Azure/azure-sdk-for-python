# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=line-too-long

from typing import Any, ClassVar, Iterable, Literal, TypedDict, Tuple, Union
from dataclasses import field, dataclass

from ._resource import (
    LocatedResource,
    generate_symbol,
    BicepStr
)

class UserIdentityProperties(TypedDict, total=False):
    clientId: BicepStr
    principalId: BicepStr


class UserAssignedIdentities(dict):
    def __init__(self, *identities: Tuple[Union[str, LocatedResource], UserIdentityProperties]):
        self._identities = identities
        super().__init__()

    def __bool__(self) -> bool:
        return bool(self._identities)

    def __repr__(self) -> str:
        return repr(self._identities)

    def items(self) -> Iterable[Tuple[Any, Any]]:
        return self._identities


@dataclass(kw_only=True)
class ManagedIdentity(LocatedResource):
    _resource: ClassVar[Literal['Microsoft.ManagedIdentity/userAssignedIdentities']] = 'Microsoft.ManagedIdentity/userAssignedIdentities'
    _version: ClassVar[str] = '2023-01-31'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("ma"), init=False, repr=False)
