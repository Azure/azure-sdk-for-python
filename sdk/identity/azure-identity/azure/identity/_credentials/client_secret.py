# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from .._internal.client_credential_base import ClientCredentialBase

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any


class ClientSecretCredential(ClientCredentialBase):
    """Authenticates as a service principal using a client secret.

    :param str tenant_id: ID of the service principal's tenant. Also called its "directory" ID.
    :param str client_id: the service principal's client ID
    :param str client_secret: one of the service principal's client secrets

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example "login.microsoftonline.com",
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    :keyword bool allow_multitenant_authentication: when True, enables the credential to acquire tokens from any tenant
        the application is registered in. When False, which is the default, the credential will acquire tokens only from
        the tenant specified by **tenant_id**.
    :keyword cache_persistence_options: configuration for persistent token caching. If unspecified, the credential
        will cache tokens in memory.
    :paramtype cache_persistence_options: ~azure.identity.TokenCachePersistenceOptions
    :keyword ~azure.identity.RegionalAuthority regional_authority: a :class:`~azure.identity.RegionalAuthority` to
        which the credential will authenticate. This argument should be used only by applications deployed to Azure
        VMs.
    """

    def __init__(self, tenant_id, client_id, client_secret, **kwargs):
        # type: (str, str, str, **Any) -> None
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
