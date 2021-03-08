# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from binascii import hexlify
from typing import TYPE_CHECKING

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.backends import default_backend
import six

from .._internal import validate_tenant_id
from .._internal.client_credential_base import ClientCredentialBase

if TYPE_CHECKING:
    from typing import Any, Optional, Union


class CertificateCredential(ClientCredentialBase):
    """Authenticates as a service principal using a certificate.

    The certificate must have an RSA private key, because this credential signs assertions using RS256.

    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    :param str client_id: the service principal's client ID
    :param str certificate_path: path to a PEM-encoded certificate file including the private key. If not provided,
          `certificate_data` is required.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
          defines authorities for other clouds.
    :keyword bytes certificate_data: the bytes of a certificate in PEM format, including the private key
    :keyword password: The certificate's password. If a unicode string, it will be encoded as UTF-8. If the certificate
          requires a different encoding, pass appropriately encoded bytes instead.
    :paramtype password: str or bytes
    :keyword bool send_certificate_chain: if True, the credential will send the public certificate chain in the x5c
          header of each token request's JWT. This is required for Subject Name/Issuer (SNI) authentication. Defaults
          to False.
    :keyword cache_persistence_options: configuration for persistent token caching. If unspecified, the credential
          will cache tokens in memory.
    :paramtype cache_persistence_options: ~azure.identity.TokenCachePersistenceOptions
    """

    def __init__(self, tenant_id, client_id, certificate_path=None, **kwargs):
        # type: (str, str, Optional[str], **Any) -> None
        validate_tenant_id(tenant_id)

        client_credential = get_client_credential(certificate_path, **kwargs)

        super(CertificateCredential, self).__init__(
            client_id=client_id, client_credential=client_credential, tenant_id=tenant_id, **kwargs
        )


def extract_cert_chain(pem_bytes):
    # type: (bytes) -> bytes
    """Extract a certificate chain from a PEM file's bytes, removing line breaks."""

    # if index raises ValueError, there's no PEM-encoded cert
    start = pem_bytes.index(b"-----BEGIN CERTIFICATE-----")
    footer = b"-----END CERTIFICATE-----"
    end = pem_bytes.rindex(footer)
    chain = pem_bytes[start : end + len(footer) + 1]

    return b"".join(chain.splitlines())


def get_client_credential(certificate_path, password=None, certificate_data=None, send_certificate_chain=False, **_):
    # type: (Optional[str], Optional[Union[bytes, str]], Optional[bytes], bool, **Any) -> dict
    """Load a certificate from a filesystem path or bytes, return it as a dict suitable for msal.ClientApplication"""

    if certificate_path:
        with open(certificate_path, "rb") as f:
            certificate_data = f.read()
    elif not certificate_data:
        raise ValueError('CertificateCredential requires a value for "certificate_path" or "certificate_data"')

    if isinstance(password, six.text_type):
        password = password.encode(encoding="utf-8")

    private_key = serialization.load_pem_private_key(certificate_data, password=password, backend=default_backend())
    if not isinstance(private_key, RSAPrivateKey):
        raise ValueError("CertificateCredential requires an RSA private key because it uses RS256 for signing")

    cert = x509.load_pem_x509_certificate(certificate_data, default_backend())
    fingerprint = cert.fingerprint(hashes.SHA1())  # nosec

    client_credential = {"private_key": certificate_data, "thumbprint": hexlify(fingerprint).decode("utf-8")}
    if password:
        client_credential["passphrase"] = password

    if send_certificate_chain:
        try:
            # the JWT needs the whole chain but load_pem_x509_certificate deserializes only the signing cert
            chain = extract_cert_chain(certificate_data)
            client_credential["public_certificate"] = six.ensure_str(chain)
        except ValueError as ex:
            # we shouldn't land here--cryptography already loaded the cert and would have raised if it were malformed
            six.raise_from(ValueError("Malformed certificate"), ex)

    return client_credential
