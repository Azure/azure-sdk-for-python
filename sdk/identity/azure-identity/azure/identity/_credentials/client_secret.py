# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from .._internal.client_credential_base import ClientCredentialBase


class ClientSecretCredential(ClientCredentialBase):
    """Authenticates as a service principal using a client secret.

    :param str tenant_id: ID of the service principal's tenant. Also called its "directory" ID.
    :param str client_id: The service principal's client ID
    :param str client_secret: One of the service principal's client secrets

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example "login.microsoftonline.com",
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    :keyword cache_persistence_options: Configuration for persistent token caching. If unspecified, the credential
        will cache tokens in memory.
    :paramtype cache_persistence_options: ~azure.identity.TokenCachePersistenceOptions
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.
    """

    def __init__(
            self,
            tenant_id: str,
            client_id: str,
            client_secret: str,
            **kwargs
    ) -> None:
        if not client_id:
            raise ValueError("client_id should be the id of an Azure Active Directory application")
        if not client_secret:
            raise ValueError("secret should be an Azure Active Directory application's client secret")
        if not tenant_id:
            raise ValueError(
                "tenant_id should be an Azure Active Directory tenant's id (also called its 'directory id')"
            )

        super(ClientSecretCredential, self).__init__(
            client_id=client_id, client_credential=client_secret, tenant_id=tenant_id, **kwargs
        )
