# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from .local_provider import LocalCryptographyProvider
from .._internal import SymmetricKey
from ... import JsonWebKey, KeyOperation, KeyType

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Union
    from .local_provider import Algorithm
    from .._internal import Key
    from ... import KeyVaultKey


class SymmetricCryptographyProvider(LocalCryptographyProvider):
    def _get_internal_key(self, key):
        # type: (Union[JsonWebKey, KeyVaultKey]) -> Key
        if isinstance(key, JsonWebKey):
            key_type = key.kty
            jwk = key
        else:
            key_type = key.key_type
            jwk = key.key

        if key_type not in (KeyType.oct, KeyType.oct_hsm):
            raise ValueError('"key" must be an oct or oct-HSM (symmetric) key')
        return SymmetricKey.from_jwk(jwk)

    def supports(self, operation, algorithm):
        # type: (KeyOperation, Algorithm) -> bool
        return (
            operation in (KeyOperation.unwrap_key, KeyOperation.wrap_key)
            and algorithm in self._internal_key.supported_key_wrap_algorithms
        )
