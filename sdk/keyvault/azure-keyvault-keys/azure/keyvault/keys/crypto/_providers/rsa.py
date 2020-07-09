# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from .local_provider import LocalCryptographyProvider
from .._internal import RsaKey
from ... import KeyOperation, KeyType

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from .._internal import Key
    from ... import KeyVaultKey

_PRIVATE_KEY_OPERATIONS = frozenset((KeyOperation.decrypt, KeyOperation.sign, KeyOperation.unwrap_key))


class RsaCryptographyProvider(LocalCryptographyProvider):
    def _get_internal_key(self, key):
        # type: (KeyVaultKey) -> Key
        if key.key_type not in (KeyType.rsa, KeyType.rsa_hsm):
            raise ValueError('"key" must be an RSA or RSA-HSM key')
        return RsaKey.from_jwk(key.key)

    def supports(self, operation):
        # type: (KeyOperation) -> bool
        if operation in _PRIVATE_KEY_OPERATIONS:
            return self._internal_key.is_private_key()
        return True
