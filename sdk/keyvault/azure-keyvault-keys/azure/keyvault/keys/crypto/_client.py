# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
from typing import TYPE_CHECKING, cast

import six
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace

from . import DecryptResult, EncryptResult, SignResult, VerifyResult, UnwrapResult, WrapResult
from ._key_validity import raise_if_time_invalid
from ._providers import get_local_cryptography_provider, NoLocalCryptography
from .. import KeyOperation
from .._models import JsonWebKey, KeyVaultKey
from .._shared import KeyVaultClientBase, parse_key_vault_id

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from datetime import datetime
    from typing import Any, Optional, Union
    from azure.core.credentials import TokenCredential
    from . import EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm
    from .._shared import KeyVaultResourceId

_LOGGER = logging.getLogger(__name__)


def _validate_arguments(operation, algorithm, **kwargs):
    # type: (KeyOperation, EncryptionAlgorithm, **Any) -> None
    """Validates the arguments passed to perform an operation with a provided algorithm.

    :param KeyOperation operation: the type of operation being requested
    :param EncryptionAlgorithm algorithm: the encryption algorithm to use for the operation
    :keyword bytes iv: initialization vector
    :keyword bytes authentication_tag: authentication tag returned from an encryption
    :keyword bytes additional_authenticated_data: data that is authenticated but not encrypted
    :raises ValueError: if parameters that are incompatible with the specified algorithm are provided.
    """
    iv = kwargs.pop("iv", None)
    tag = kwargs.pop("tag", None)
    aad = kwargs.pop("aad", None)

    if operation == KeyOperation.encrypt:
        if iv and "CBC" not in algorithm:
            raise ValueError(
                "iv should only be provided with AES-CBC algorithms; {} does not accept an iv".format(algorithm)
            )
        if iv is None and "CBC" in algorithm:
            raise ValueError("iv is a required parameter for encryption with AES-CBC algorithms.")
        if aad and not ("CBC" in algorithm or "GCM" in algorithm):
            raise ValueError(
                "additional_authenticated_data should only be provided with AES algorithms; {} does not accept "
                "additional authenticated data".format(algorithm)
            )

    if operation == KeyOperation.decrypt:
        if iv and not ("CBC" in algorithm or "GCM" in algorithm):
            raise ValueError(
                "iv should only be provided with AES algorithms; {} does not accept an iv".format(algorithm)
            )
        if iv is None and ("CBC" in algorithm or "GCM" in algorithm):
            raise ValueError("iv is a required parameter for decryption with AES algorithms.")
        if tag and "GCM" not in algorithm:
            raise ValueError(
                "authentication_tag should only be provided with AES-GCM algorithms; {} does not accept a tag".format(
                    algorithm
                )
            )
        if tag is None and "GCM" in algorithm:
            raise ValueError("authentication_tag is a required parameter for AES-GCM decryption.")
        if aad and not ("CBC" in algorithm or "GCM" in algorithm):
            raise ValueError(
                "additional_authenticated_data should only be provided with AES algorithms; {} does not accept "
                "additional authenticated data".format(algorithm)
            )


class CryptographyClient(KeyVaultClientBase):
    """Performs cryptographic operations using Azure Key Vault keys.

    This client will perform operations locally when it's intialized with the necessary key material or is able to get
    that material from Key Vault. When the required key material is unavailable, cryptographic operations are performed
    by the Key Vault service.

    :param key:
        Either a :class:`~azure.keyvault.keys.KeyVaultKey` instance as returned by
        :func:`~azure.keyvault.keys.KeyClient.get_key`, or a string.
        If a string, the value must be the identifier of an Azure Key Vault key. Including a version is recommended.
    :type key: str or :class:`~azure.keyvault.keys.KeyVaultKey`
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity`
    :keyword api_version: version of the Key Vault API to use. Defaults to the most recent.
    :paramtype api_version: ~azure.keyvault.keys.ApiVersion
    :keyword transport: transport to use.
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
        self._jwk = kwargs.pop("_jwk", False)
        self._not_before = None  # type: Optional[datetime]
        self._expires_on = None  # type: Optional[datetime]
        self._key_id = None  # type: Optional[KeyVaultResourceId]

        if isinstance(key, KeyVaultKey):
            self._key = key.key  # type: Union[JsonWebKey, KeyVaultKey, str, None]
            self._key_id = parse_key_vault_id(key.id)
            if key.properties._attributes:  # pylint:disable=protected-access
                self._not_before = key.properties.not_before
                self._expires_on = key.properties.expires_on
        elif isinstance(key, six.string_types):
            self._key = None
            self._key_id = parse_key_vault_id(key)
            if self._key_id.version is None:
                self._key_id.version = ""  # to avoid an error and get the latest version when getting the key
            self._keys_get_forbidden = False
        elif self._jwk:
            self._key = key
        else:
            raise ValueError("'key' must be a KeyVaultKey instance or a key ID string")

        if self._jwk:
            try:
                self._local_provider = get_local_cryptography_provider(cast(JsonWebKey, self._key))
                self._initialized = True
            except Exception as ex:  # pylint:disable=broad-except
                six.raise_from(ValueError("The provided jwk is not valid for local cryptography"), ex)
        else:
            self._local_provider = NoLocalCryptography()
            self._initialized = False

        self._vault_url = None if (self._jwk or self._key_id is None) else self._key_id.vault_url  # type: ignore
        super(CryptographyClient, self).__init__(
            vault_url=self._vault_url or "vault_url", credential=credential, **kwargs
        )

    @property
    def key_id(self):
        # type: () -> Optional[str]
        """The full identifier of the client's key.

        This property may be None when a client is constructed with :func:`from_jwk`.

        :rtype: str or None
        """
        if not self._jwk:
            return self._key_id.source_id if self._key_id else None
        return cast(JsonWebKey, self._key).kid  # type: ignore[attr-defined]

    @property
    def vault_url(self):  # type: ignore
        # type: () -> Optional[str]
        """The base vault URL of the client's key.

        This property may be None when a client is constructed with :func:`from_jwk`.

        :rtype: str or None
        """
        return self._vault_url

    @classmethod
    def from_jwk(cls, jwk):
        # type: (Union[JsonWebKey, dict]) -> CryptographyClient
        """Creates a client that can only perform cryptographic operations locally.

        :param jwk: the key's cryptographic material, as a JsonWebKey or dictionary.
        :type jwk: JsonWebKey or dict
        :rtype: CryptographyClient
        """
        if not isinstance(jwk, JsonWebKey):
            jwk = JsonWebKey(**jwk)
        return cls(jwk, object(), _jwk=True)  # type: ignore

    @distributed_trace
    def _initialize(self, **kwargs):
        # type: (**Any) -> None
        if self._initialized:
            return

        # try to get the key material, if we don't have it and aren't forbidden to do so
        if not (self._key or self._keys_get_forbidden):
            try:
                key_bundle = self._client.get_key(
                    self._key_id.vault_url if self._key_id else None,
                    self._key_id.name if self._key_id else None,
                    self._key_id.version if self._key_id else None,
                    **kwargs
                )
                key = KeyVaultKey._from_key_bundle(key_bundle)  # pylint:disable=protected-access
                self._key = key.key
                self._key_id = parse_key_vault_id(key.id)  # update the key ID in case we didn't have the version before
            except HttpResponseError as ex:
                # if we got a 403, we don't have keys/get permission and won't try to get the key again
                # (other errors may be transient)
                self._keys_get_forbidden = ex.status_code == 403

        # if we have the key material, create a local crypto provider with it
        if self._key:
            self._local_provider = get_local_cryptography_provider(cast(JsonWebKey, self._key))
            self._initialized = True
        else:
            # try to get the key again next time unless we know we're forbidden to do so
            self._initialized = self._keys_get_forbidden

    @distributed_trace
    def encrypt(self, algorithm, plaintext, **kwargs):
        # type: (EncryptionAlgorithm, bytes, **Any) -> EncryptResult
        """Encrypt bytes using the client's key.

        Requires the keys/encrypt permission. This method encrypts only a single block of data, whose size depends on
        the key and encryption algorithm.

        :param algorithm: encryption algorithm to use
        :type algorithm: :class:`~azure.keyvault.keys.crypto.EncryptionAlgorithm`
        :param bytes plaintext: bytes to encrypt
        :keyword bytes iv: initialization vector. Required for only AES-CBC(PAD) encryption.
        :keyword bytes additional_authenticated_data: optional data that is authenticated but not encrypted. For use
            with AES-GCM encryption.
        :rtype: :class:`~azure.keyvault.keys.crypto.EncryptResult`
        :raises ValueError: if parameters that are incompatible with the specified algorithm are provided.

        .. literalinclude:: ../tests/test_examples_crypto.py
            :start-after: [START encrypt]
            :end-before: [END encrypt]
            :caption: Encrypt bytes
            :language: python
            :dedent: 8
        """
        iv = kwargs.pop("iv", None)
        aad = kwargs.pop("additional_authenticated_data", None)
        _validate_arguments(operation=KeyOperation.encrypt, algorithm=algorithm, iv=iv, aad=aad)
        self._initialize(**kwargs)

        if self._local_provider.supports(KeyOperation.encrypt, algorithm):
            raise_if_time_invalid(self._not_before, self._expires_on)
            try:
                return self._local_provider.encrypt(algorithm, plaintext, iv=iv)
            except Exception as ex:  # pylint:disable=broad-except
                _LOGGER.warning("Local encrypt operation failed: %s", ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG))
                if self._jwk:
                    raise
        elif self._jwk:
            raise NotImplementedError(
                'This key does not support the "encrypt" operation with algorithm "{}"'.format(algorithm)
            )

        operation_result = self._client.encrypt(
            vault_base_url=self._key_id.vault_url if self._key_id else None,
            key_name=self._key_id.name if self._key_id else None,
            key_version=self._key_id.version if self._key_id else None,
            parameters=self._models.KeyOperationsParameters(algorithm=algorithm, value=plaintext, iv=iv, aad=aad),
            **kwargs
        )

        result_iv = operation_result.iv if hasattr(operation_result, "iv") else None
        result_tag = operation_result.authentication_tag if hasattr(operation_result, "authentication_tag") else None
        result_aad = (
            operation_result.additional_authenticated_data
            if hasattr(operation_result, "additional_authenticated_data")
            else None
        )

        return EncryptResult(
            key_id=self.key_id,
            algorithm=algorithm,
            ciphertext=operation_result.result,
            iv=result_iv,
            authentication_tag=result_tag,
            additional_authenticated_data=result_aad,
        )

    @distributed_trace
    def decrypt(self, algorithm, ciphertext, **kwargs):
        # type: (EncryptionAlgorithm, bytes, **Any) -> DecryptResult
        """Decrypt a single block of encrypted data using the client's key.

        Requires the keys/decrypt permission. This method decrypts only a single block of data, whose size depends on
        the key and encryption algorithm.

        :param algorithm: encryption algorithm to use
        :type algorithm: :class:`~azure.keyvault.keys.crypto.EncryptionAlgorithm`
        :param bytes ciphertext: encrypted bytes to decrypt
        :keyword bytes iv: the initialization vector used during encryption. Required for AES decryption.
        :keyword bytes authentication_tag: the authentication tag generated during encryption. Required for only AES-GCM
            decryption.
        :keyword bytes additional_authenticated_data: optional data that is authenticated but not encrypted. For use
            with AES-GCM decryption.
        :rtype: :class:`~azure.keyvault.keys.crypto.DecryptResult`
        :raises ValueError: if parameters that are incompatible with the specified algorithm are provided.

        .. literalinclude:: ../tests/test_examples_crypto.py
            :start-after: [START decrypt]
            :end-before: [END decrypt]
            :caption: Decrypt bytes
            :language: python
            :dedent: 8
        """
        iv = kwargs.pop("iv", None)
        tag = kwargs.pop("authentication_tag", None)
        aad = kwargs.pop("additional_authenticated_data", None)
        _validate_arguments(operation=KeyOperation.decrypt, algorithm=algorithm, iv=iv, tag=tag, aad=aad)
        self._initialize(**kwargs)

        if self._local_provider.supports(KeyOperation.decrypt, algorithm):
            try:
                return self._local_provider.decrypt(algorithm, ciphertext, iv=iv)
            except Exception as ex:  # pylint:disable=broad-except
                _LOGGER.warning("Local decrypt operation failed: %s", ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG))
                if self._jwk:
                    raise
        elif self._jwk:
            raise NotImplementedError(
                'This key does not support the "decrypt" operation with algorithm "{}"'.format(algorithm)
            )

        operation_result = self._client.decrypt(
            vault_base_url=self._key_id.vault_url if self._key_id else None,
            key_name=self._key_id.name if self._key_id else None,
            key_version=self._key_id.version if self._key_id else None,
            parameters=self._models.KeyOperationsParameters(
                algorithm=algorithm, value=ciphertext, iv=iv, tag=tag, aad=aad
            ),
            **kwargs
        )

        return DecryptResult(key_id=self.key_id, algorithm=algorithm, plaintext=operation_result.result)

    @distributed_trace
    def wrap_key(self, algorithm, key, **kwargs):
        # type: (KeyWrapAlgorithm, bytes, **Any) -> WrapResult
        """Wrap a key with the client's key.

        Requires the keys/wrapKey permission.

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
            raise_if_time_invalid(self._not_before, self._expires_on)
            try:
                return self._local_provider.wrap_key(algorithm, key)
            except Exception as ex:  # pylint:disable=broad-except
                _LOGGER.warning("Local wrap operation failed: %s", ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG))
                if self._jwk:
                    raise
        elif self._jwk:
            raise NotImplementedError(
                'This key does not support the "wrapKey" operation with algorithm "{}"'.format(algorithm)
            )

        operation_result = self._client.wrap_key(
            vault_base_url=self._key_id.vault_url if self._key_id else None,
            key_name=self._key_id.name if self._key_id else None,
            key_version=self._key_id.version if self._key_id else None,
            parameters=self._models.KeyOperationsParameters(algorithm=algorithm, value=key),
            **kwargs
        )

        return WrapResult(key_id=self.key_id, algorithm=algorithm, encrypted_key=operation_result.result)

    @distributed_trace
    def unwrap_key(self, algorithm, encrypted_key, **kwargs):
        # type: (KeyWrapAlgorithm, bytes, **Any) -> UnwrapResult
        """Unwrap a key previously wrapped with the client's key.

        Requires the keys/unwrapKey permission.

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
                if self._jwk:
                    raise
        elif self._jwk:
            raise NotImplementedError(
                'This key does not support the "unwrapKey" operation with algorithm "{}"'.format(algorithm)
            )

        operation_result = self._client.unwrap_key(
            vault_base_url=self._key_id.vault_url if self._key_id else None,
            key_name=self._key_id.name if self._key_id else None,
            key_version=self._key_id.version if self._key_id else None,
            parameters=self._models.KeyOperationsParameters(algorithm=algorithm, value=encrypted_key),
            **kwargs
        )
        return UnwrapResult(key_id=self.key_id, algorithm=algorithm, key=operation_result.result)

    @distributed_trace
    def sign(self, algorithm, digest, **kwargs):
        # type: (SignatureAlgorithm, bytes, **Any) -> SignResult
        """Create a signature from a digest using the client's key.

        Requires the keys/sign permission.

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
            raise_if_time_invalid(self._not_before, self._expires_on)
            try:
                return self._local_provider.sign(algorithm, digest)
            except Exception as ex:  # pylint:disable=broad-except
                _LOGGER.warning("Local sign operation failed: %s", ex, exc_info=_LOGGER.isEnabledFor(logging.DEBUG))
                if self._jwk:
                    raise
        elif self._jwk:
            raise NotImplementedError(
                'This key does not support the "sign" operation with algorithm "{}"'.format(algorithm)
            )

        operation_result = self._client.sign(
            vault_base_url=self._key_id.vault_url if self._key_id else None,
            key_name=self._key_id.name if self._key_id else None,
            key_version=self._key_id.version if self._key_id else None,
            parameters=self._models.KeySignParameters(algorithm=algorithm, value=digest),
            **kwargs
        )

        return SignResult(key_id=self.key_id, algorithm=algorithm, signature=operation_result.result)

    @distributed_trace
    def verify(self, algorithm, digest, signature, **kwargs):
        # type: (SignatureAlgorithm, bytes, bytes, **Any) -> VerifyResult
        """Verify a signature using the client's key.

        Requires the keys/verify permission.

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
                if self._jwk:
                    raise
        elif self._jwk:
            raise NotImplementedError(
                'This key does not support the "verify" operation with algorithm "{}"'.format(algorithm)
            )

        operation_result = self._client.verify(
            vault_base_url=self._key_id.vault_url if self._key_id else None,
            key_name=self._key_id.name if self._key_id else None,
            key_version=self._key_id.version if self._key_id else None,
            parameters=self._models.KeyVerifyParameters(algorithm=algorithm, digest=digest, signature=signature),
            **kwargs
        )

        return VerifyResult(key_id=self.key_id, algorithm=algorithm, is_valid=operation_result.value)
