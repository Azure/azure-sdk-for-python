# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import cast, Optional, Union, TYPE_CHECKING

from cryptography.hazmat.primitives.asymmetric.padding import AsymmetricPadding, OAEP, PKCS1v15, PSS, MGF1
from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateKey,
    RSAPrivateNumbers,
    RSAPublicKey,
    RSAPublicNumbers,
)
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.hashes import Hash, HashAlgorithm, SHA1, SHA256, SHA384, SHA512
from cryptography.hazmat.primitives.serialization import Encoding, KeySerializationEncryption, PrivateFormat

from ._enums import EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm

if TYPE_CHECKING:
    # Import clients only during TYPE_CHECKING to avoid circular dependency
    from ._client import CryptographyClient
    from .._client import KeyClient


SIGN_ALGORITHM_MAP = {
    SHA256: SignatureAlgorithm.rs256,
    SHA384: SignatureAlgorithm.rs384,
    SHA512: SignatureAlgorithm.rs512,
}
OAEP_MAP = {
    SHA1: EncryptionAlgorithm.rsa_oaep,
    SHA256: EncryptionAlgorithm.rsa_oaep_256
}
PSS_MAP = {
    SignatureAlgorithm.rs256: SignatureAlgorithm.ps256,
    SignatureAlgorithm.rs384: SignatureAlgorithm.ps384,
    SignatureAlgorithm.rs512: SignatureAlgorithm.ps512,
}


class ManagedRsaKey(RSAPrivateKey):
    """An `RSAPrivateKey` implementation based on a key managed by Key Vault.

    :param str key_name: The name of the key vault key to use.
    :param key_client: The client that will be used to communicate with Key Vault.
    :type key_client: KeyClient
    """

    def __init__(self, key_name: str, key_client: "KeyClient") -> None:  # pylint:disable=unused-argument
        self._key_name: str = key_name
        self._key_client: "KeyClient" = key_client
        self._crypto_client: "CryptographyClient" = key_client.get_cryptography_client(key_name)

    def decrypt(self, ciphertext: bytes, padding: AsymmetricPadding) -> bytes:
        """Decrypts the provided ciphertext.

        :param bytes ciphertext: Encrypted bytes to decrypt.
        :param padding: The padding to use. Supported paddings are `OAEP` and `PKCS1v15`. For `OAEP` padding, supported
            hash algorithms are `SHA1` and `SHA256`. The only supported mask generation function is `MGF1`. See
            https://learn.microsoft.com/azure/key-vault/keys/about-keys-details for details.
        :type padding: AsymmetricPadding

        :returns: The decrypted plaintext, as bytes.
        :rtype: bytes
        """
        if isinstance(padding, OAEP):
            # Public algorithm property was only added in https://github.com/pyca/cryptography/pull/9582
            # _algorithm property has been available in every version of the OAEP class, so we use it as a backup
            try:
                algorithm = padding.algorithm
            except AttributeError:
                algorithm = padding._algorithm
            mapped_algorithm = OAEP_MAP.get(type(algorithm))
            if mapped_algorithm is None:
                raise ValueError(f"Unsupported algorithm: {algorithm.name}")
    
            # Public mgf property was added at the same time as algorithm
            try:
                mgf = padding.mgf
            except AttributeError:
                mgf = padding._mgf
            if not isinstance(mgf, MGF1):
                raise ValueError(f"Unsupported MGF: {mgf}")
        elif isinstance(padding, PKCS1v15):
            mapped_algorithm = EncryptionAlgorithm.rsa1_5
        else:
            raise ValueError(f"Unsupported padding: {padding.name}")
        result = self._crypto_client.decrypt(mapped_algorithm, ciphertext)
        return result.plaintext

    @property
    def key_size(self) -> int:
        """The bit length of the public modulus.

        :returns: The key's size.
        :rtype: int
        """
        key = self._key_client.get_key(self._key_name)
        return int.from_bytes(key.key.n, "big").bit_length()  # type: ignore[attr-defined]

    def public_key(self) -> RSAPublicKey:
        """The `RSAPublicKey` associated with this private key.

        :returns: The `RSAPublicKey` associated with the key.
        :rtype: RSAPublicKey
        """
        key = self._key_client.get_key(self._key_name)
        e = int.from_bytes(key.key.e, "big")  # type: ignore[attr-defined]
        n = int.from_bytes(key.key.n, "big")  # type: ignore[attr-defined]
        public_numbers = RSAPublicNumbers(e, n)
        return public_numbers.public_key()

    def sign(
        self,
        data: bytes,
        padding: AsymmetricPadding,
        algorithm: Union[Prehashed, HashAlgorithm],
    ) -> bytes:
        """Signs the data.

        :param bytes data: The data to sign, as bytes.
        :param padding: The padding to use. Supported paddings are `PKCS1v15` and `PSS`. For `PSS`, the only supported
            mask generation function is `MGF1`. See https://learn.microsoft.com/azure/key-vault/keys/about-keys-details
            for details.
        :type padding: AsymmetricPadding
        :param algorithm: The algorithm to sign with. Only `HashAlgorithm`s are supported -- specifically, `SHA256`,
            `SHA384`, and `SHA512`.
        :type algorithm: Prehashed or HashAlgorithm

        :returns: The signature, as bytes.
        :rtype: bytes
        """
        if isinstance(algorithm, Prehashed):
            raise ValueError("`Prehashed` algorithms are unsupported. Please provide a `HashAlgorithm` instead.")

        mapped_algorithm = SIGN_ALGORITHM_MAP.get(type(algorithm))
        if mapped_algorithm is None:
            raise ValueError(f"Unsupported algorithm: {algorithm.name}")

        # If PSS padding is requested, use the PSS equivalent algorithm
        if isinstance(padding, PSS):
            mapped_algorithm = PSS_MAP.get(type(mapped_algorithm))

            # Public mgf property was only added in https://github.com/pyca/cryptography/pull/9582
            # _mgf property has been available in every version of the PSS class, so we use it as a backup
            try:
                mgf = padding.mgf
            except AttributeError:
                mgf = padding._mgf
            if not isinstance(mgf, MGF1):
                raise ValueError(f"Unsupported MGF: {mgf}")

        # The only other padding accepted is PKCS1v15
        elif not isinstance(padding, PKCS1v15):
            raise ValueError(f"Unsupported padding: {padding.name}")

        digest = Hash(algorithm)
        digest.update(data)
        result = self._crypto_client.sign(cast(SignatureAlgorithm, mapped_algorithm), digest.finalize())
        return result.signature

    def private_numbers(self) -> RSAPrivateNumbers:  # pylint:disable=docstring-missing-return,docstring-missing-rtype
        """Returns an RSAPrivateNumbers. Not implemented, as the private key is managed by Key Vault."""
        raise NotImplementedError()

    def private_bytes(  # pylint:disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
        self,
        encoding: Encoding,
        format: PrivateFormat,
        encryption_algorithm: KeySerializationEncryption,
    ) -> bytes:
        """Returns the key serialized as bytes. Not implemented, as the private key is managed by Key Vault."""
        raise NotImplementedError()


class DecryptResult:
    """The result of a decrypt operation.

    :param str key_id: The encryption key's Key Vault identifier
    :param algorithm: The encryption algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.EncryptionAlgorithm
    :param bytes plaintext: The decrypted bytes
    """

    def __init__(self, key_id: Optional[str], algorithm: EncryptionAlgorithm, plaintext: bytes) -> None:
        self.key_id = key_id
        self.algorithm = algorithm
        self.plaintext = plaintext


class EncryptResult:
    """The result of an encrypt operation.

    :param str key_id: The encryption key's Key Vault identifier
    :param algorithm: The encryption algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.EncryptionAlgorithm
    :param bytes ciphertext: The encrypted bytes

    :keyword bytes iv: Initialization vector for symmetric algorithms
    :keyword bytes authentication_tag: The tag to authenticate when performing decryption with an authenticated
        algorithm
    :keyword bytes additional_authenticated_data: Additional data to authenticate but not encrypt/decrypt when using an
        authenticated algorithm
    """

    def __init__(self, key_id: Optional[str], algorithm: EncryptionAlgorithm, ciphertext: bytes, **kwargs) -> None:
        self.key_id = key_id
        self.algorithm = algorithm
        self.ciphertext = ciphertext
        self.iv = kwargs.pop("iv", None)
        self.tag = kwargs.pop("authentication_tag", None)
        self.aad = kwargs.pop("additional_authenticated_data", None)


class SignResult:
    """The result of a sign operation.

    :param str key_id: The signing key's Key Vault identifier
    :param algorithm: The signature algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.SignatureAlgorithm
    :param bytes signature:
    """

    def __init__(self, key_id: Optional[str], algorithm: SignatureAlgorithm, signature: bytes) -> None:
        self.key_id = key_id
        self.algorithm = algorithm
        self.signature = signature


class VerifyResult:
    """The result of a verify operation.

    :param str key_id: The signing key's Key Vault identifier
    :param bool is_valid: Whether the signature is valid
    :param algorithm: The signature algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.SignatureAlgorithm
    """

    def __init__(self, key_id: Optional[str], is_valid: bool, algorithm: SignatureAlgorithm) -> None:
        self.key_id = key_id
        self.is_valid = is_valid
        self.algorithm = algorithm


class UnwrapResult:
    """The result of an unwrap key operation.

    :param str key_id: Key encryption key's Key Vault identifier
    :param algorithm: The key wrap algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.KeyWrapAlgorithm
    :param bytes key: The unwrapped key
    """

    def __init__(self, key_id: Optional[str], algorithm: KeyWrapAlgorithm, key: bytes) -> None:
        self.key_id = key_id
        self.algorithm = algorithm
        self.key = key


class WrapResult:
    """The result of a wrap key operation.

    :param str key_id: The wrapping key's Key Vault identifier
    :param algorithm: The key wrap algorithm used
    :type algorithm: ~azure.keyvault.keys.crypto.KeyWrapAlgorithm
    :param bytes encrypted_key: The encrypted key bytes
    """

    def __init__(self, key_id: Optional[str], algorithm: KeyWrapAlgorithm, encrypted_key: bytes) -> None:
        self.key_id = key_id
        self.algorithm = algorithm
        self.encrypted_key = encrypted_key
