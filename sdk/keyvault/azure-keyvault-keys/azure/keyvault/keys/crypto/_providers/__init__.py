# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from .ec import EllipticCurveCryptographyProvider
from .local_provider import LocalCryptographyProvider
from .rsa import RsaCryptographyProvider
from .symmetric import SymmetricCryptographyProvider
from ... import KeyType

if TYPE_CHECKING:
    from ... import JsonWebKey


def get_local_cryptography_provider(key):
    # type: (JsonWebKey) -> LocalCryptographyProvider
    if key.kty in (KeyType.ec, KeyType.ec_hsm):
        return EllipticCurveCryptographyProvider(key)
    if key.kty in (KeyType.rsa, KeyType.rsa_hsm):
        return RsaCryptographyProvider(key)
    if key.kty in (KeyType.oct, KeyType.oct_hsm):
        return SymmetricCryptographyProvider(key)

    raise ValueError('Unsupported key type "{}"'.format(key.kty))


class NoLocalCryptography(LocalCryptographyProvider):
    def __init__(self):  # pylint:disable=super-init-not-called
        return

    def supports(self, operation, algorithm):
        return False

    def _get_internal_key(self, key):
        return None
