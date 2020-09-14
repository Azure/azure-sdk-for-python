# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from .local_provider import LocalCryptographyProvider
from .._internal import SymmetricKey
from ... import KeyOperation, KeyType

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from .local_provider import Algorithm
    from .._internal import Key
    from ... import KeyVaultKey


class SymmetricCryptographyProvider(LocalCryptographyProvider):
    def _get_internal_key(self, key):
        # type: (KeyVaultKey) -> Key
        if key.key_type != KeyType.oct:
            raise ValueError('"key" must be an oct (symmetric) key')
        return SymmetricKey.from_jwk(key.key)

    def supports(self, operation, algorithm):
        # type: (KeyOperation, Algorithm) -> bool
        return (
            operation in (KeyOperation.unwrap_key, KeyOperation.wrap_key)
            and algorithm in self._internal_key.supported_key_wrap_algorithms
        )
