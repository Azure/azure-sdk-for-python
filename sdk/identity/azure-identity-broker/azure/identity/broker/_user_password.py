# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any
import msal
from azure.identity._credentials import (
    UsernamePasswordCredential as _UsernamePasswordCredential,
)  # pylint:disable=protected-access
from ._utils import resolve_tenant


class UsernamePasswordBrokerCredential(_UsernamePasswordCredential):
    """Authenticates a user with a username and password.

    In general, Microsoft doesn't recommend this kind of authentication, because it's less secure than other
    authentication flows.

    Authentication with this credential is not interactive, so it is **not compatible with any form of
    multi-factor authentication or consent prompting**. The application must already have consent from the user or
    a directory admin.

    This credential can only authenticate work and school accounts; Microsoft accounts are not supported.
    See `Microsoft Entra ID documentation
    <https://learn.microsoft.com/azure/active-directory/fundamentals/sign-up-organization>`_ for more information about
    account types.

    :param str client_id: The application's client ID
    :param str username: The user's username (usually an email address)
    :param str password: The user's password

    :keyword str authority: Authority of a Microsoft Entra endpoint, for example "login.microsoftonline.com",
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    :keyword str tenant_id: Tenant ID or a domain associated with a tenant. If not provided, defaults to the
        "organizations" tenant, which supports only Microsoft Entra work or school accounts.
    :keyword cache_persistence_options: Configuration for persistent token caching. If unspecified, the credential
        will cache tokens in memory.
    :paramtype cache_persistence_options: ~azure.identity.TokenCachePersistenceOptions
    :keyword bool disable_instance_discovery: Determines whether or not instance discovery is performed when attempting
        to authenticate. Setting this to true will completely disable both instance discovery and authority validation.
        This functionality is intended for use in scenarios where the metadata endpoint cannot be reached, such as in
        private clouds or Azure Stack. The process of instance discovery entails retrieving authority metadata from
        https://login.microsoft.com/ to validate the authority. By setting this to **True**, the validation of the
        authority is disabled. As a result, it is crucial to ensure that the configured authority host is valid and
        trustworthy.
    :keyword bool allow_broker: An authentication broker is an application that runs on a user's machine that manages
        the authentication handshakes and token maintenance for connected accounts. The Windows operating system uses
        the Web Account Manager (WAM) as its authentication broker. If this parameter is set to True, the broker will
        be used when possible. Defaults to True.
        Check https://learn.microsoft.com/azure/active-directory/develop/scenario-desktop-acquire-token-wam for more
        information about WAM.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.
    """

    def __init__(self, client_id: str, username: str, password: str, **kwargs: Any) -> None:
        # The base class will accept an AuthenticationRecord, allowing this credential to authenticate silently the
        # first time it's asked for a token. However, we want to ensure this first authentication is not silent, to
        # validate the given password. This class therefore doesn't document the authentication_record argument, and we
        # discard it here.
        self._allow_broker = kwargs.pop("allow_broker", True)
        super(UsernamePasswordBrokerCredential, self).__init__(
            client_id=client_id, username=username, password=password, **kwargs
        )

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
