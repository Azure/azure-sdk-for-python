# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from .local_provider import LocalCryptographyProvider
from .._internal import EllipticCurveKey
from ... import KeyOperation, KeyType

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from .._internal import Key
    from ... import KeyVaultKey


class EllipticCurveCryptographyProvider(LocalCryptographyProvider):
    def _get_internal_key(self, key):
        # type: (KeyVaultKey) -> Key
        if key.key_type not in (KeyType.ec, KeyType.ec_hsm):
            raise ValueError('"key" must be an EC or EC-HSM key')
        return EllipticCurveKey.from_jwk(key.key)

    def supports(self, operation):
        # type: (KeyOperation) -> bool
        if operation == KeyOperation.sign:
            return self._internal_key.is_private_key()
        return operation == KeyOperation.verify
