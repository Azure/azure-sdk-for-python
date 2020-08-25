# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime, timedelta, tzinfo

import six
from azure.core.exceptions import AzureError, HttpResponseError
from azure.core.tracing.decorator import distributed_trace

from . import DecryptResult, EncryptResult, SignResult, VerifyResult, UnwrapResult, WrapResult
from ._internal import EllipticCurveKey, RsaKey, SymmetricKey
from .._models import KeyVaultKey
from .._shared import KeyVaultClientBase, parse_vault_id

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Optional, Union
    from azure.core.credentials import TokenCredential
    from . import EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm
    from ._internal import Key as _Key


class _UTC_TZ(tzinfo):
    """from https://docs.python.org/2/library/datetime.html#tzinfo-objects"""

    ZERO = timedelta(0)

    def utcoffset(self, dt):
        return self.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return self.ZERO


_UTC = _UTC_TZ()


def _enforce_nbf_exp(key):
    # type: (KeyVaultKey) -> None
    try:
        nbf = key.properties.not_before
        exp = key.properties.expires_on
    except AttributeError:
        # we consider the key valid because a user must have deliberately created it
        # (if it came from Key Vault, it would have those attributes)
        return

    now = datetime.now(_UTC)
    if (nbf and exp) and not nbf <= now <= exp:
        raise ValueError("This client's key is useable only between {} and {} (UTC)".format(nbf, exp))
    if nbf and nbf >= now:
        raise ValueError("This client's key is not useable until {} (UTC)".format(nbf))
    if exp and exp <= now:
        raise ValueError("This client's key expired at {} (UTC)".format(exp))


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

    Creating a ``CryptographyClient``:

    .. code-block:: python

        from azure.identity import DefaultAzureCredential
        from azure.keyvault.keys.crypto import CryptographyClient

        credential = DefaultAzureCredential()

        # create a CryptographyClient using a KeyVaultKey instance
        key = key_client.get_key("mykey")
        crypto_client = CryptographyClient(key, credential)

        # or a key's id, which must include a version
        key_id = "https://<your vault>.vault.azure.net/keys/mykey/fe4fdcab688c479a9aa80f01ffeac26"
        crypto_client = CryptographyClient(key_id, credential)

    """

    def __init__(self, key, credential, **kwargs):
        # type: (Union[KeyVaultKey, str], TokenCredential, **Any) -> None

        if isinstance(key, KeyVaultKey):
            self._key = key
            self._key_id = parse_vault_id(key.id)
            self._allowed_ops = frozenset(self._key.key_operations)
        elif isinstance(key, six.string_types):
            self._key = None
            self._key_id = parse_vault_id(key)
            self._keys_get_forbidden = None  # type: Optional[bool]

            # will be replaced with actual permissions before any local operations are attempted, if we can get the key
            self._allowed_ops = frozenset()
        else:
            raise ValueError("'key' must be a KeyVaultKey instance or a key ID string including a version")

        if not self._key_id.version:
            raise ValueError("'key' must include a version")

        self._internal_key = None  # type: Optional[_Key]

        super(CryptographyClient, self).__init__(vault_url=self._key_id.vault_url, credential=credential, **kwargs)

    @property
    def key_id(self):
        # type: () -> str
        """The full identifier of the client's key.

        :rtype: str
        """
        return "/".join(self._key_id)

    @distributed_trace
    def _get_key(self, **kwargs):
        # type: (**Any) -> Optional[KeyVaultKey]
        """Get the client's :class:`~azure.keyvault.keys.KeyVaultKey`.

        Can be ``None``, if the client lacks keys/get permission.

        :rtype: :class:`~azure.keyvault.keys.KeyVaultKey` or ``None``
        """

        if not (self._key or self._keys_get_forbidden):
            try:
                self._key = self._client.get_key(
                    self._key_id.vault_url, self._key_id.name, self._key_id.version, **kwargs
                )
                self._allowed_ops = frozenset(self._key.key_operations)
            except HttpResponseError as ex:
                # if we got a 403, we don't have keys/get permission and won't try to get the key again
                # (other errors may be transient)
                self._keys_get_forbidden = ex.status_code == 403
        return self._key

    def _get_local_key(self, **kwargs):
        # type: (**Any) -> Optional[_Key]
        """Gets an object implementing local operations. Will be ``None``, if the client was instantiated with a key
        id and lacks keys/get permission."""

        if not self._internal_key:
            key = self._get_key(**kwargs)
            if not key:
                return None

            kty = key.key_type.lower()
            if kty.startswith("ec"):
                self._internal_key = EllipticCurveKey.from_jwk(key.key)
            elif kty.startswith("rsa"):
                self._internal_key = RsaKey.from_jwk(key.key)
            elif kty == "oct":
                self._internal_key = SymmetricKey.from_jwk(key.key)
            else:
                raise ValueError("Unsupported key type '{}'".format(key.key_type))

        return self._internal_key

    @distributed_trace
    def encrypt(self, algorithm, plaintext, **kwargs):
        # type: (EncryptionAlgorithm, bytes, **Any) -> EncryptResult
        """Encrypt bytes using the client's key. Requires the keys/encrypt permission.

        This method encrypts only a single block of data, whose size depends on the key and encryption algorithm.

        :param algorithm: encryption algorithm to use
        :type algorithm: :class:`~azure.keyvault.keys.crypto.EncryptionAlgorithm`
        :param bytes plaintext: bytes to encrypt
        :rtype: :class:`~azure.keyvault.keys.crypto.EncryptResult`

        Example:

        .. code-block:: python

            from azure.keyvault.keys.crypto import EncryptionAlgorithm

            # the result holds the ciphertext and identifies the encryption key and algorithm used
            result = client.encrypt(EncryptionAlgorithm.rsa_oaep, b"plaintext")
            ciphertext = result.ciphertext
            print(result.key_id)
            print(result.algorithm)

        """

        local_key = self._get_local_key(**kwargs)
        if local_key:
            _enforce_nbf_exp(self._key)
            if "encrypt" not in self._allowed_ops:
                raise AzureError("This client doesn't have 'keys/encrypt' permission")
            result = local_key.encrypt(plaintext, algorithm=algorithm.value)
        else:

            parameters = self._models.KeyOperationsParameters(
                algorithm=algorithm,
                value=plaintext
            )

            result = self._client.encrypt(
                vault_base_url=self._key_id.vault_url,
                key_name=self._key_id.name,
                key_version=self._key_id.version,
                parameters=parameters,
                **kwargs
            ).result
        return EncryptResult(key_id=self.key_id, algorithm=algorithm, ciphertext=result)

    @distributed_trace
    def decrypt(self, algorithm, ciphertext, **kwargs):
        # type: (EncryptionAlgorithm, bytes, **Any) -> DecryptResult
        """Decrypt a single block of encrypted data using the client's key. Requires the keys/decrypt permission.

        This method decrypts only a single block of data, whose size depends on the key and encryption algorithm.

        :param algorithm: encryption algorithm to use
        :type algorithm: :class:`~azure.keyvault.keys.crypto.EncryptionAlgorithm`
        :param bytes ciphertext: encrypted bytes to decrypt
        :rtype: :class:`~azure.keyvault.keys.crypto.DecryptResult`

        Example:

        .. code-block:: python

            from azure.keyvault.keys.crypto import EncryptionAlgorithm

            result = client.decrypt(EncryptionAlgorithm.rsa_oaep, ciphertext)
            print(result.plaintext)

        """

        parameters = self._models.KeyOperationsParameters(
            algorithm=algorithm,
            value=ciphertext
        )
        result = self._client.decrypt(
            vault_base_url=self._key_id.vault_url,
            key_name=self._key_id.name,
            key_version=self._key_id.version,
            parameters=parameters,
            **kwargs
        )
        return DecryptResult(key_id=self.key_id, algorithm=algorithm, plaintext=result.result)

    @distributed_trace
    def wrap_key(self, algorithm, key, **kwargs):
        # type: (KeyWrapAlgorithm, bytes, **Any) -> WrapResult
        """Wrap a key with the client's key. Requires the keys/wrapKey permission.

        :param algorithm: wrapping algorithm to use
        :type algorithm: :class:`~azure.keyvault.keys.crypto.KeyWrapAlgorithm`
        :param bytes key: key to wrap
        :rtype: :class:`~azure.keyvault.keys.crypto.WrapResult`

        Example:

        .. code-block:: python

            from azure.keyvault.keys.crypto import KeyWrapAlgorithm

            # the result holds the encrypted key and identifies the encryption key and algorithm used
            result = client.wrap_key(KeyWrapAlgorithm.rsa_oaep, key_bytes)
            encrypted_key = result.encrypted_key
            print(result.key_id)
            print(result.algorithm)

        """

        local_key = self._get_local_key(**kwargs)
        if local_key:
            _enforce_nbf_exp(self._key)
            if "wrapKey" not in self._allowed_ops:
                raise AzureError("This client doesn't have 'keys/wrapKey' permission")
            result = local_key.wrap_key(key, algorithm=algorithm.value)
        else:
            parameters = self._models.KeyOperationsParameters(
                algorithm=algorithm,
                value=key,
            )
            result = self._client.wrap_key(
                self._key_id.vault_url,
                self._key_id.name,
                self._key_id.version,
                parameters=parameters
            ).result

        return WrapResult(key_id=self.key_id, algorithm=algorithm, encrypted_key=result)

    @distributed_trace
    def unwrap_key(self, algorithm, encrypted_key, **kwargs):
        # type: (KeyWrapAlgorithm, bytes, **Any) -> UnwrapResult
        """Unwrap a key previously wrapped with the client's key. Requires the keys/unwrapKey permission.

        :param algorithm: wrapping algorithm to use
        :type algorithm: :class:`~azure.keyvault.keys.crypto.KeyWrapAlgorithm`
        :param bytes encrypted_key: the wrapped key
        :rtype: :class:`~azure.keyvault.keys.crypto.UnwrapResult`

        Example:

        .. code-block:: python

            from azure.keyvault.keys.crypto import KeyWrapAlgorithm

            result = client.unwrap_key(KeyWrapAlgorithm.rsa_oaep, wrapped_bytes)
            key = result.key

        """
        local_key = self._get_local_key(**kwargs)
        if local_key and local_key.is_private_key():
            if "unwrapKey" not in self._allowed_ops:
                raise AzureError("This client doesn't have 'keys/unwrapKey' permission")
            result = local_key.unwrap_key(encrypted_key, **kwargs)
        else:

            parameters = self._models.KeyOperationsParameters(
                algorithm=algorithm,
                value=encrypted_key
            )

            result = self._client.unwrap_key(
                vault_base_url=self._key_id.vault_url,
                key_name=self._key_id.name,
                key_version=self._key_id.version,
                parameters=parameters,
                **kwargs
            ).result
        return UnwrapResult(key_id=self._key_id, algorithm=algorithm, key=result)

    @distributed_trace
    def sign(self, algorithm, digest, **kwargs):
        # type: (SignatureAlgorithm, bytes, **Any) -> SignResult
        """Create a signature from a digest using the client's key. Requires the keys/sign permission.

        :param algorithm: signing algorithm
        :type algorithm: :class:`~azure.keyvault.keys.crypto.SignatureAlgorithm`
        :param bytes digest: hashed bytes to sign
        :rtype: :class:`~azure.keyvault.keys.crypto.SignResult`

        Example:

        .. code-block:: python

            import hashlib
            from azure.keyvault.keys.crypto import SignatureAlgorithm

            digest = hashlib.sha256(b"plaintext").digest()

            # sign returns a tuple with the signature and the metadata required to verify it
            result = client.sign(SignatureAlgorithm.rs256, digest)

            # the result contains the signature and identifies the key and algorithm used
            signature = result.signature
            print(result.key_id)
            print(result.algorithm)

        """

        parameters = self._models.KeySignParameters(
            algorithm=algorithm,
            value=digest
        )

        result = self._client.sign(
            vault_base_url=self._key_id.vault_url,
            key_name=self._key_id.name,
            key_version=self._key_id.version,
            parameters=parameters,
            **kwargs
        )
        return SignResult(key_id=self.key_id, algorithm=algorithm, signature=result.result)

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

        Example:

        .. code-block:: python

            from azure.keyvault.keys.crypto import SignatureAlgorithm

            verified = client.verify(SignatureAlgorithm.rs256, digest, signature)
            assert verified.is_valid

        """

        local_key = self._get_local_key(**kwargs)
        if local_key:
            if "verify" not in self._allowed_ops:
                raise AzureError("This client doesn't have 'keys/verify' permission")
            result = local_key.verify(digest, signature, algorithm=algorithm.value)
        else:
            parameters = self._models.KeyVerifyParameters(
                algorithm=algorithm,
                digest=digest,
                signature=signature
            )

            result = self._client.verify(
                vault_base_url=self._key_id.vault_url,
                key_name=self._key_id.name,
                key_version=self._key_id.version,
                parameters=parameters,
                **kwargs
            ).value
        return VerifyResult(key_id=self.key_id, algorithm=algorithm, is_valid=result)
