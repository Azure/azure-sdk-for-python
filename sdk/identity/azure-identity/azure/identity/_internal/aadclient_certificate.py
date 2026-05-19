# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
from typing import Optional, Union
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.backends import default_backend


class AadClientCertificate:
    """Wraps 'cryptography' to provide the crypto operations AadClient requires for certificate authentication.

    :param pem_bytes: PEM-encoded certificate including the (RSA) private key. May be ``bytes`` or a ``str``;
        ``str`` values are encoded as UTF-8 before being handed to ``cryptography``.
    :paramtype pem_bytes: bytes or str
    :param password: (optional) the certificate's password. May be ``bytes`` or a ``str``; ``str`` values are
        encoded as UTF-8.
    :paramtype password: bytes or str or None
    """

    def __init__(self, pem_bytes: Union[bytes, str], password: Optional[Union[bytes, str]] = None) -> None:
        if isinstance(pem_bytes, str):
            pem_bytes = pem_bytes.encode("utf-8")
        if isinstance(password, str):
            password = password.encode("utf-8")
        private_key = serialization.load_pem_private_key(pem_bytes, password=password, backend=default_backend())
        if not isinstance(private_key, RSAPrivateKey):
            raise ValueError("The certificate must have an RSA private key because RS256 is used for signing")
        self._private_key = private_key

        cert = x509.load_pem_x509_certificate(pem_bytes, default_backend())
        fingerprint = cert.fingerprint(hashes.SHA1())  # nosec # CodeQL [SM02167] only used as a thumbprint/identifier
        sha256_fingerprint = cert.fingerprint(hashes.SHA256())
        self._thumbprint = base64.urlsafe_b64encode(fingerprint).decode("utf-8")
        self._sha256_thumbprint = base64.urlsafe_b64encode(sha256_fingerprint).decode("utf-8")

    @property
    def thumbprint(self) -> str:
        """The certificate's SHA1 thumbprint as a base64url-encoded string.

        :rtype: str
        """
        return self._thumbprint

    @property
    def sha256_thumbprint(self) -> str:
        """The certificate's SHA256 thumbprint as a base64url-encoded string.

        :rtype: str
        """
        return self._sha256_thumbprint

    def sign_rs256(self, plaintext: bytes) -> bytes:
        """Sign bytes using RS256.

        :param bytes plaintext: Bytes to sign.
        :return: The signature.
        :rtype: bytes
        """
        return self._private_key.sign(
            plaintext, padding.PKCS1v15(), hashes.SHA256()  # CodeQL [SM04457] need this for backwards compatibility
        )

    def sign_ps256(self, plaintext: bytes) -> bytes:
        """Sign bytes using PS256.

        :param bytes plaintext: Bytes to sign.
        :return: The signature.
        :rtype: bytes
        """
        hash_alg = hashes.SHA256()

        # Note: For PS265, the salt length should match the hash output size, so we use the hash algorithm's
        # digest_size property to get the correct value.
        return self._private_key.sign(
            plaintext,
            padding.PSS(mgf=padding.MGF1(hash_alg), salt_length=hash_alg.digest_size),
            hash_alg,
        )
