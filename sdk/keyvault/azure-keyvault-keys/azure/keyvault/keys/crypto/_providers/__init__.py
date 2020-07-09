# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from .ec import EllipticCurveCryptographyProvider
from .rsa import RsaCryptographyProvider
from .symmetric import SymmetricCryptographyProvider
from ... import KeyType

if TYPE_CHECKING:
    from .local_provider import LocalCryptographyProvider
    from ... import KeyVaultKey


def get_local_cryptography_provider(key):
    # type: (KeyVaultKey) -> LocalCryptographyProvider
    if key.key_type in (KeyType.ec, KeyType.ec_hsm):
        return EllipticCurveCryptographyProvider(key)
    if key.key_type in (KeyType.rsa, KeyType.rsa_hsm):
        return RsaCryptographyProvider(key)
    if key.key_type == KeyType.oct:
        return SymmetricCryptographyProvider(key)

    raise ValueError('Unsupported key type "{}"'.format(key.key_type))
