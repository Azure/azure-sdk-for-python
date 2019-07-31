# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Optional, Union
    from azure.core.credentials import TokenCredential
    from . import EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm

from azure.core.exceptions import HttpResponseError
import six

from . import DecryptResult, EncryptResult, SignResult, VerifyResult, UnwrapKeyResult, WrapKeyResult
from ..models import Key
from .._shared import KeyVaultClientBase, parse_vault_id


class CryptographyClient(KeyVaultClientBase):
    """
    **Keyword arguments:**

    *api_version:* version of the Key Vault API to use. Defaults to the most recent.
    """

    def __init__(self, key, credential, **kwargs):
        # type: (Union[Key, str], TokenCredential, Any) -> None

        if isinstance(key, Key):
            self._key = key
            self._key_id = parse_vault_id(key.id)
        elif isinstance(key, six.text_type):
            self._key = None
            self._key_id = parse_vault_id(key)
            self._get_key_forbidden = None  # type: Optional[bool]
        else:
            raise ValueError("'key' must be a Key instance or a key ID string including a version")

        if not self._key_id.version:
            raise ValueError("'key' must include a version")

        super(CryptographyClient, self).__init__(vault_url=self._key_id.vault_url, credential=credential, **kwargs)

    @property
    def key_id(self):
        # type: () -> str
        return "/".join(self._key_id)

    @property
    def key(self):
        # type: () -> Optional[Key]
        """The Key used by this client. Will be `None`, if the client lacks keys/get permission."""

        if not (self._key or self._get_key_forbidden):
            try:
                self._key = self._client.get_key(self._key_id.vault_url, self._key_id.name, self._key_id.version)
            except HttpResponseError as ex:
                self._get_key_forbidden = ex.status_code == 403
        return self._key

    def encrypt(self, plaintext, algorithm, **kwargs):
        # type: (bytes, EncryptionAlgorithm, Any) -> EncryptResult
        """
        **Keyword arguments:**

        *authentication_data*: used by authenticated encryption algorithms e.g. AES-GCM, AESCBC-HMAC
        *iv*: initialization vector, required for some algorithms e.g. AESCBC
        """

        result = self._client.encrypt(
            self._key_id.vault_url, self._key_id.name, self._key_id.version, algorithm, plaintext, **kwargs
        )
        return EncryptResult(key_id=self.key_id, algorithm=algorithm, ciphertext=result.result, authentication_tag=None)

    def decrypt(self, ciphertext, algorithm, **kwargs):
        # type: (bytes, EncryptionAlgorithm, Any) -> bytes
        """
        **Keyword arguments:**

        *authentication_data*: used by authenticated encryption algorithms e.g. AES-GCM, AESCBC-HMAC
        *authentication_tag*
        *iv*: initialization vector, required for some algorithms e.g. AES
        """

        authentication_data = kwargs.pop("authentication_data", None)
        authentication_tag = kwargs.pop("authentication_tag", None)
        if authentication_data and not authentication_tag:
            raise ValueError("'authentication_tag' is required when 'authentication_data' is specified")

        result = self._client.decrypt(
            self._key_id.vault_url, self._key_id.name, self._key_id.version, algorithm, ciphertext, **kwargs
        )
        return result.result

    def wrap(self, key, algorithm, **kwargs):
        # type: (bytes, KeyWrapAlgorithm, Any) -> WrapKeyResult
        """
        """

        result = self._client.wrap_key(
            self._key_id.vault_url, self._key_id.name, self._key_id.version, algorithm=algorithm, value=key, **kwargs
        )
        return WrapKeyResult(key_id=self.key_id, algorithm=algorithm, encrypted_key=result.result)

    def unwrap(self, encrypted_key, algorithm, **kwargs):
        # type: (bytes, KeyWrapAlgorithm, Any) -> bytes
        """
        """

        result = self._client.unwrap_key(
            self._key_id.vault_url,
            self._key_id.name,
            self._key_id.version,
            algorithm=algorithm,
            value=encrypted_key,
            **kwargs
        )
        return result.result

    def sign(self, digest, algorithm, **kwargs):
        # type: (bytes, SignatureAlgorithm, Any) -> SignResult
        """
        """

        result = self._client.sign(
            self._key_id.vault_url, self._key_id.name, self._key_id.version, algorithm, digest, **kwargs
        )
        return SignResult(key_id=self.key_id, algorithm=algorithm, signature=result.result)

    def verify(self, digest, signature, algorithm, **kwargs):
        # type: (bytes, bytes, SignatureAlgorithm, Any) -> bool
        """
        """

        result = self._client.verify(
            self._key_id.vault_url, self._key_id.name, self._key_id.version, algorithm, digest, signature, **kwargs
        )
        return result.value
