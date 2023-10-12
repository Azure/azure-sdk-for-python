# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import socket
from typing import Dict, Any
import msal

from azure.core.exceptions import ClientAuthenticationError
from azure.identity._credentials import (
    InteractiveBrowserCredential as _InteractiveBrowserCredential,
)  # pylint:disable=protected-access
from azure.identity._exceptions import CredentialUnavailableError  # pylint:disable=protected-access
from azure.identity._internal.utils import within_dac  # pylint:disable=protected-access
from ._utils import wrap_exceptions, resolve_tenant


class InteractiveBrowserBrokerCredential(_InteractiveBrowserCredential):
    """Opens a browser to interactively authenticate a user.

    :func:`~get_token` opens a browser to a login URL provided by Azure Active Directory and authenticates a user
    there with the authorization code flow, using PKCE (Proof Key for Code Exchange) internally to protect the code.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example "login.microsoftonline.com",
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    :keyword str tenant_id: an Azure Active Directory tenant ID. Defaults to the "organizations" tenant, which can
        authenticate work or school accounts.
    :keyword str client_id: Client ID of the Azure Active Directory application users will sign in to. If
        unspecified, users will authenticate to an Azure development application.
    :keyword str login_hint: a username suggestion to pre-fill the login page's username/email address field. A user
        may still log in with a different username.
    :keyword str redirect_uri: a redirect URI for the application identified by `client_id` as configured in Azure
        Active Directory, for example "http://localhost:8400". This is only required when passing a value for
        **client_id**, and must match a redirect URI in the application's registration. The credential must be able to
        bind a socket to this URI.
    :keyword AuthenticationRecord authentication_record: :class:`AuthenticationRecord` returned by :func:`authenticate`
    :keyword bool disable_automatic_authentication: if True, :func:`get_token` will raise
        :class:`AuthenticationRequiredError` when user interaction is required to acquire a token. Defaults to False.
    :keyword cache_persistence_options: configuration for persistent token caching. If unspecified, the credential
        will cache tokens in memory.
    :paramtype cache_persistence_options: ~azure.identity.TokenCachePersistenceOptions
    :keyword int timeout: seconds to wait for the user to complete authentication. Defaults to 300 (5 minutes).
    :keyword bool allow_broker: An authentication broker is an application that runs on a user's machine that manages
        the authentication handshakes and token maintenance for connected accounts. The Windows operating system uses
        the Web Account Manager (WAM) as its authentication broker. If this parameter is set to True, the broker will
        be used when possible. Defaults to True.
        Check https://learn.microsoft.com/azure/active-directory/develop/scenario-desktop-acquire-token-wam for more
        information about WAM.
    :keyword int parent_window_handle: If your app is a GUI app running on a modern Windows system,
        and your app opts in to use broker via `allow_broker`, you are required to also provide its window handle,
        so that the sign in UI window will properly pop up on top of your window.
    :keyword bool enable_msa_passthrough: Determines whether Microsoft Account (MSA) passthrough is enabled. Note, this
        is only needed for select legacy first-party applications. Defaults to False.
    :keyword bool disable_instance_discovery: Determines whether or not instance discovery is performed when attempting
        to authenticate. Setting this to true will completely disable both instance discovery and authority validation.
        This functionality is intended for use in scenarios where the metadata endpoint cannot be reached, such as in
        private clouds or Azure Stack. The process of instance discovery entails retrieving authority metadata from
        https://login.microsoft.com/ to validate the authority. By setting this to **True**, the validation of the
        authority is disabled. As a result, it is crucial to ensure that the configured authority host is valid and
        trustworthy.
    :raises ValueError: invalid **redirect_uri**
    """

    def __init__(self, **kwargs: Any) -> None:
        self._allow_broker = kwargs.pop("allow_broker", True)
        self._parent_window_handle = kwargs.pop("parent_window_handle", None)
        self._enable_msa_passthrough = kwargs.pop("enable_msa_passthrough", False)
        super().__init__(**kwargs)

    @wrap_exceptions
    def _request_token(self, *scopes: str, **kwargs: Any) -> Dict:
        scopes = list(scopes)  # type: ignore
        claims = kwargs.get("claims")
        app = self._get_app(**kwargs)
        port = self._parsed_url.port if self._parsed_url else None

        try:
            result = app.acquire_token_interactive(
                scopes=scopes,
                login_hint=self._login_hint,
                claims_challenge=claims,
                timeout=self._timeout,
                prompt="select_account",
                port=port,
                parent_window_handle=self._parent_window_handle,
                enable_msa_passthrough=self._enable_msa_passthrough,
            )
        except socket.error as ex:
            raise CredentialUnavailableError(message="Couldn't start an HTTP server.") from ex
        if "access_token" not in result and "error_description" in result:
            if within_dac.get():
                raise CredentialUnavailableError(message=result["error_description"])
            raise ClientAuthenticationError(message=result.get("error_description"))
        if "access_token" not in result:
            if within_dac.get():
                raise CredentialUnavailableError(message="Failed to authenticate user")
            raise ClientAuthenticationError(message="Failed to authenticate user")

        # base class will raise for other errors
        return result

    def _get_app(self, **kwargs: Any) -> msal.ClientApplication:
        tenant_id = resolve_tenant(
            self._tenant_id, additionally_allowed_tenants=self._additionally_allowed_tenants, **kwargs
        )

        client_applications_map = self._client_applications
        capabilities = None
        token_cache = self._cache

        app_class = msal.ConfidentialClientApplication if self._client_credential else msal.PublicClientApplication

        if kwargs.get("enable_cae"):
            client_applications_map = self._cae_client_applications
            capabilities = ["CP1"]
            token_cache = self._cae_cache

        if not token_cache:
            token_cache = self._initialize_cache(is_cae=bool(kwargs.get("enable_cae")))

        if tenant_id not in client_applications_map:
            client_applications_map[tenant_id] = app_class(
                client_id=self._client_id,
                client_credential=self._client_credential,
                client_capabilities=capabilities,
                authority="{}/{}".format(self._authority, tenant_id),
                azure_region=self._regional_authority,
                token_cache=token_cache,
                http_client=self._client,
                instance_discovery=self._instance_discovery,
                allow_broker=self._allow_broker,
            )

        return client_applications_map[tenant_id]
