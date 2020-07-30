# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from binascii import hexlify
import time
from typing import TYPE_CHECKING

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import msal
import six

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .._internal.decorators import wrap_exceptions
from .._internal.msal_credentials import MsalCredential
from .._internal.proactive_refresh import ProactiveRefresh

if TYPE_CHECKING:
    from typing import Any


class CertificateCredential(MsalCredential, ProactiveRefresh):
    """Authenticates as a service principal using a certificate.

    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    :param str client_id: the service principal's client ID
    :param str certificate_path: path to a PEM-encoded certificate file including the private key.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
          defines authorities for other clouds.
    :keyword password: The certificate's password. If a unicode string, it will be encoded as UTF-8. If the certificate
          requires a different encoding, pass appropriately encoded bytes instead.
    :paramtype password: str or bytes
    :keyword bool enable_persistent_cache: if True, the credential will store tokens in a persistent cache. Defaults to
          False.
    :keyword bool allow_unencrypted_cache: if True, the credential will fall back to a plaintext cache when encryption
          is unavailable. Default to False. Has no effect when `enable_persistent_cache` is False.
    """

    def __init__(self, tenant_id, client_id, certificate_path, **kwargs):
        # type: (str, str, str, **Any) -> None
        if not certificate_path:
            raise ValueError(
                "'certificate_path' must be the path to a PEM file containing an x509 certificate and its private key"
            )

        password = kwargs.pop("password", None)
        if isinstance(password, six.text_type):
            password = password.encode(encoding="utf-8")

        with open(certificate_path, "rb") as f:
            pem_bytes = f.read()

        cert = x509.load_pem_x509_certificate(pem_bytes, default_backend())
        fingerprint = cert.fingerprint(hashes.SHA1())  # nosec

        # TODO: msal doesn't formally support passwords (but soon will); the below depends on an implementation detail
        private_key = serialization.load_pem_private_key(pem_bytes, password=password, backend=default_backend())
        super(CertificateCredential, self).__init__(
            client_id=client_id,
            client_credential={"private_key": private_key, "thumbprint": hexlify(fingerprint).decode("utf-8")},
            tenant_id=tenant_id,
            **kwargs
        )

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
          attribute gives a reason. Any error response from Azure Active Directory is available as the error's
          ``response`` attribute.
        """
        return self._get_token_impl(*scopes, **kwargs)

    @wrap_exceptions
    def _acquire_token_silently(self, *scopes, **kwargs):
        # type: (*str, **Any) -> Optional[AccessToken]
        """Default implementation suitable for confidential clients."""
        app = self._get_app()
        request_time = int(time.time())
        result = app.acquire_token_silent_with_error(list(scopes), account=None, **kwargs)
        if result and "access_token" in result and "expires_in" in result:
            return AccessToken(result["access_token"], request_time + int(result["expires_in"]))
        return None

    @wrap_exceptions
    def _request_token(self, *scopes, **kwargs):
        app = self._get_app()
        request_time = int(time.time())
        result = app.acquire_token_for_client(list(scopes))
        if "access_token" not in result:
            message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
            raise ClientAuthenticationError(message=message)

        return AccessToken(result["access_token"], request_time + int(result["expires_in"]))

    def _get_app(self):
        # type: () -> msal.ConfidentialClientApplication
        if not self._msal_app:
            self._msal_app = self._create_app(msal.ConfidentialClientApplication)
        return self._msal_app
