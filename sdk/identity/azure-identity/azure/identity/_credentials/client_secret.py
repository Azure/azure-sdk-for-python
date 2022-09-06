# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from .._internal.client_credential_base import ClientCredentialBase


class ClientSecretCredential(ClientCredentialBase):
    """Authenticates as a service principal using a client secret.

    :param str tenant_id: ID of the service principal's tenant. Also called its "directory" ID.
    :param str client_id: the service principal's client ID
    :param str client_secret: one of the service principal's client secrets

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example "login.microsoftonline.com",
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    :keyword cache_persistence_options: configuration for persistent token caching. If unspecified, the credential
        will cache tokens in memory.
    :paramtype cache_persistence_options: ~azure.identity.TokenCachePersistenceOptions
    :keyword bool allow_broker: Brokers provide single sign-on, device identification, and application identification
        verification. If this parameter is set to True, the broker will be used when possible. Defaults to False.
    """

    def __init__(
            self,
            tenant_id: str,
            client_id: str,
            client_secret: str,
            *,
            allow_broker: bool = False,
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
            client_id=client_id,
            client_credential=client_secret,
            tenant_id=tenant_id,
            allow_broker=allow_broker,
            **kwargs
        )
