# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
from typing import TYPE_CHECKING

import six
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace

from . import DecryptResult, EncryptResult, SignResult, VerifyResult, UnwrapResult, WrapResult
from ._key_validity import raise_if_time_invalid
from ._providers import get_local_cryptography_provider, NoLocalCryptography
from .. import KeyOperation
from .._models import KeyVaultKey
from .._shared import KeyVaultClientBase, parse_vault_id

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Optional, Union
    from azure.core.credentials import TokenCredential
    from . import EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm

_LOGGER = logging.getLogger(__name__)


class CryptographyClient(KeyVaultClientBase):
    """Performs cryptographic operations using Azure Key Vault keys.

    :param key:
        Either a :class:`~azure.keyvault.keys.KeyVaultKey` instance as returned by
        :func:`~azure.keyvault.keys.KeyClient.get_key`, or a string.
        If a string, the value must be the full identifier of an Azure Key Vault key with a version.
    :type key: str or :class:`~azure.keyvault.keys.KeyVaultKey`
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`
    :keyword api_version: version of the Key Vault API to use. Defaults to the most recent.
    :paramtype api_version: ~azure.keyvault.keys.ApiVersion
    :keyword transport: transport to use. Defaults to :class:`~azure.core.pipeline.transport.RequestsTransport`.
    :paramtype transport: ~azure.core.pipeline.transport.HttpTransport

    .. literalinclude:: ../tests/test_examples_crypto.py
        :start-after: [START create_client]
        :end-before: [END create_client]
        :caption: Create a CryptographyClient
        :language: python
        :dedent: 8
    """

    def __init__(self, key, credential, **kwargs):
        # type: (Union[KeyVaultKey, str], TokenCredential, **Any) -> None

        if isinstance(key, KeyVaultKey):
            self._key = key
            self._key_id = parse_vault_id(key.id)
        elif isinstance(key, six.string_types):
            self._key = None
            self._key_id = parse_vault_id(key)
            self._keys_get_forbidden = None  # type: Optional[bool]
        else:
            raise ValueError("'key' must be a KeyVaultKey instance or a key ID string including a version")

        if not self._key_id.version:
            raise ValueError("'key' must include a version")

        self._local_provider = NoLocalCryptography()
        self._initialized = False

        super(CryptographyClient, self).__init__(vault_url=self._key_id.vault_url, credential=credential, **kwargs)

    @property
    def key_id(self):
        # type: () -> str
        """The full identifier of the client's key.

        :rtype: str
        """
        return "/".join(self._key_id)

    @distributed_trace
    def _initialize(self, **kwargs):
        # type: (**Any) -> None
        if self._initialized:
            return

        # try to get the key material, if we don't have it and aren't forbidden to do so
        if not (self._key or self._keys_get_forbidden):
            try:
                self._key = self._client.get_key(
                    self._key_id.vault_url, self._key_id.name, self._key_id.version, **kwargs
                )
            except HttpResponseError as ex:
                # if we got a 403, we don't have keys/get permission and won't try to get the key again
                # (other errors may be transient)
                self._keys_get_forbidden = ex.status_code == 403

        # if we have the key material, create a local crypto provider with it
        if self._key:
            self._local_provider = get_local_cryptography_provider(self._key)
            self._initialized = True
        else:
            # try to get the key again next time unless we know we're forbidden to do so
            self._initialized = self._keys_get_forbidden

    @distributed_trace
    def encrypt(self, algorithm, plaintext, **kwargs):
        # type: (EncryptionAlgorithm, bytes, **Any) -> EncryptResult
        """Encrypt bytes using the client's key. Requires the keys/encrypt permission.

        This method encrypts only a single block of data, whose size depends on the key and encryption algorithm.

        :param algorithm: encryption algorithm to use
        :type algorithm: :class:`~azure.keyvault.keys.crypto.EncryptionAlgorithm`
        :param bytes plaintext: bytes to encrypt
        :rtype: :class:`~azure.keyvault.keys.crypto.EncryptResult`

        .. literalinclude:: ../tests/test_examples_crypto.py
            :start-after: [START encrypt]
            :end-before: [END encrypt]
            :caption: Encrypt bytes
            :language: python
            :dedent: 8
        """
        self._initialize(**kwargs)
        if self._local_provider.supports(KeyOperation.encrypt, algorithm):
            raise_if_time_invalid(self._key)
            try:
                return self._local_provider.encrypt(algorithm, plaintext)
            except Exception as ex:  # pylint:disable=broad-except
                _LOGGER.warning("Local encrypt operation failed: %s", ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG))

        operation_result = self._client.encrypt(
            vault_base_url=self._key_id.vault_url,
            key_name=self._key_id.name,
            key_version=self._key_id.version,
            parameters=self._models.KeyOperationsParameters(algorithm=algorithm, value=plaintext),
            **kwargs
        )

        return EncryptResult(key_id=self.key_id, algorithm=algorithm, ciphertext=operation_result.result)

    @distributed_trace
    def decrypt(self, algorithm, ciphertext, **kwargs):
        # type: (EncryptionAlgorithm, bytes, **Any) -> DecryptResult
        """Decrypt a single block of encrypted data using the client's key. Requires the keys/decrypt permission.

        This method decrypts only a single block of data, whose size depends on the key and encryption algorithm.

        :param algorithm: encryption algorithm to use
        :type algorithm: :class:`~azure.keyvault.keys.crypto.EncryptionAlgorithm`
        :param bytes ciphertext: encrypted bytes to decrypt
        :rtype: :class:`~azure.keyvault.keys.crypto.DecryptResult`

        .. literalinclude:: ../tests/test_examples_crypto.py
            :start-after: [START decrypt]
            :end-before: [END decrypt]
            :caption: Decrypt bytes
            :language: python
            :dedent: 8
        """
        self._initialize(**kwargs)
        if self._local_provider.supports(KeyOperation.decrypt, algorithm):
            try:
                return self._local_provider.decrypt(algorithm, ciphertext)
            except Exception as ex:  # pylint:disable=broad-except
                _LOGGER.warning("Local decrypt operation failed: %s", ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG))

        operation_result = self._client.decrypt(
            vault_base_url=self._key_id.vault_url,
            key_name=self._key_id.name,
            key_version=self._key_id.version,
            parameters=self._models.KeyOperationsParameters(algorithm=algorithm, value=ciphertext),
            **kwargs
        )

        return DecryptResult(key_id=self.key_id, algorithm=algorithm, plaintext=operation_result.result)

    @distributed_trace
    def wrap_key(self, algorithm, key, **kwargs):
        # type: (KeyWrapAlgorithm, bytes, **Any) -> WrapResult
        """Wrap a key with the client's key. Requires the keys/wrapKey permission.

        :param algorithm: wrapping algorithm to use
        :type algorithm: :class:`~azure.keyvault.keys.crypto.KeyWrapAlgorithm`
        :param bytes key: key to wrap
        :rtype: :class:`~azure.keyvault.keys.crypto.WrapResult`

        .. literalinclude:: ../tests/test_examples_crypto.py
            :start-after: [START wrap_key]
            :end-before: [END wrap_key]
            :caption: Wrap a key
            :language: python
            :dedent: 8
        """
        self._initialize(**kwargs)
        if self._local_provider.supports(KeyOperation.wrap_key, algorithm):
            raise_if_time_invalid(self._key)
            try:
                return self._local_provider.wrap_key(algorithm, key)
            except Exception as ex:  # pylint:disable=broad-except
                _LOGGER.warning("Local wrap operation failed: %s", ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG))

        operation_result = self._client.wrap_key(
            vault_base_url=self._key_id.vault_url,
            key_name=self._key_id.name,
            key_version=self._key_id.version,
            parameters=self._models.KeyOperationsParameters(algorithm=algorithm, value=key),
            **kwargs
        )

        return WrapResult(key_id=self.key_id, algorithm=algorithm, encrypted_key=operation_result.result)

    @distributed_trace
    def unwrap_key(self, algorithm, encrypted_key, **kwargs):
        # type: (KeyWrapAlgorithm, bytes, **Any) -> UnwrapResult
        """Unwrap a key previously wrapped with the client's key. Requires the keys/unwrapKey permission.

        :param algorithm: wrapping algorithm to use
        :type algorithm: :class:`~azure.keyvault.keys.crypto.KeyWrapAlgorithm`
        :param bytes encrypted_key: the wrapped key
        :rtype: :class:`~azure.keyvault.keys.crypto.UnwrapResult`

        .. literalinclude:: ../tests/test_examples_crypto.py
            :start-after: [START unwrap_key]
            :end-before: [END unwrap_key]
            :caption: Unwrap a key
            :language: python
            :dedent: 8
        """
        self._initialize(**kwargs)
        if self._local_provider.supports(KeyOperation.unwrap_key, algorithm):
            try:
                return self._local_provider.unwrap_key(algorithm, encrypted_key)
            except Exception as ex:  # pylint:disable=broad-except
                _LOGGER.warning("Local unwrap operation failed: %s", ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG))

        operation_result = self._client.unwrap_key(
            vault_base_url=self._key_id.vault_url,
            key_name=self._key_id.name,
            key_version=self._key_id.version,
            parameters=self._models.KeyOperationsParameters(algorithm=algorithm, value=encrypted_key),
            **kwargs
        )
        return UnwrapResult(key_id=self._key_id, algorithm=algorithm, key=operation_result.result)

    @distributed_trace
    def sign(self, algorithm, digest, **kwargs):
        # type: (SignatureAlgorithm, bytes, **Any) -> SignResult
        """Create a signature from a digest using the client's key. Requires the keys/sign permission.

        :param algorithm: signing algorithm
        :type algorithm: :class:`~azure.keyvault.keys.crypto.SignatureAlgorithm`
        :param bytes digest: hashed bytes to sign
        :rtype: :class:`~azure.keyvault.keys.crypto.SignResult`

        .. literalinclude:: ../tests/test_examples_crypto.py
            :start-after: [START sign]
            :end-before: [END sign]
            :caption: Sign bytes
            :language: python
            :dedent: 8
        """
        self._initialize(**kwargs)
        if self._local_provider.supports(KeyOperation.sign, algorithm):
            raise_if_time_invalid(self._key)
            try:
                return self._local_provider.sign(algorithm, digest)
            except Exception as ex:  # pylint:disable=broad-except
                _LOGGER.warning("Local sign operation failed: %s", ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG))

        operation_result = self._client.sign(
            vault_base_url=self._key_id.vault_url,
            key_name=self._key_id.name,
            key_version=self._key_id.version,
            parameters=self._models.KeySignParameters(algorithm=algorithm, value=digest),
            **kwargs
        )

        return SignResult(key_id=self.key_id, algorithm=algorithm, signature=operation_result.result)

    @distributed_trace
    def verify(self, algorithm, digest, signature, **kwargs):
        # type: (SignatureAlgorithm, bytes, bytes, **Any) -> VerifyResult
        """Verify a signature using the client's key. Requires the keys/verify permission.

        :param algorithm: verification algorithm
        :type algorithm: :class:`~azure.keyvault.keys.crypto.SignatureAlgorithm`
        :param bytes digest: Pre-hashed digest corresponding to **signature**. The hash algorithm used must be
          compatible with **algorithm**.
        :param bytes signature: signature to verify
        :rtype: :class:`~azure.keyvault.keys.crypto.VerifyResult`

        .. literalinclude:: ../tests/test_examples_crypto.py
            :start-after: [START verify]
            :end-before: [END verify]
            :caption: Verify a signature
            :language: python
            :dedent: 8
        """
        self._initialize(**kwargs)
        if self._local_provider.supports(KeyOperation.verify, algorithm):
            try:
                return self._local_provider.verify(algorithm, digest, signature)
            except Exception as ex:  # pylint:disable=broad-except
                _LOGGER.warning("Local verify operation failed: %s", ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG))

        operation_result = self._client.verify(
            vault_base_url=self._key_id.vault_url,
            key_name=self._key_id.name,
            key_version=self._key_id.version,
            parameters=self._models.KeyVerifyParameters(algorithm=algorithm, digest=digest, signature=signature),
            **kwargs
        )

        return VerifyResult(key_id=self.key_id, algorithm=algorithm, is_valid=operation_result.value)
