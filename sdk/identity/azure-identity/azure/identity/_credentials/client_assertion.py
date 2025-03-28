# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Callable, Any

from .._internal.client_credential_base import ClientCredentialBase


class ClientAssertionCredential(ClientCredentialBase):
    """Authenticates a service principal with a JWT assertion.

    This credential is for advanced scenarios. :class:`~azure.identity.CertificateCredential` has a more
    convenient API for the most common assertion scenario, authenticating a service principal with a certificate.

    :param str tenant_id: ID of the principal's tenant. Also called its "directory" ID.
    :param str client_id: The principal's client ID
    :param func: A callable that returns a string assertion. The credential will call this every time it
        acquires a new token.
    :paramtype func: Callable[[], str]

    :keyword str authority: Authority of a Microsoft Entra endpoint, for example
        "login.microsoftonline.com", the authority for Azure Public Cloud (which is the default).
        :class:`~azure.identity.AzureAuthorityHosts` defines authorities for other clouds.
    :keyword cache_persistence_options: configuration for persistent token caching. If unspecified, the credential
        will cache tokens in memory.
    :paramtype cache_persistence_options: ~azure.identity.TokenCachePersistenceOptions
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START create_client_assertion_credential]
            :end-before: [END create_client_assertion_credential]
            :language: python
            :dedent: 4
            :caption: Create a ClientAssertionCredential.
    """

    def __init__(self, tenant_id: str, client_id: str, func: Callable[[], str], **kwargs: Any) -> None:
        client_credential = {
            "client_assertion": func,
        }
        cache = kwargs.pop("cache", None)
        cae_cache = kwargs.pop("cae_cache", None)
        super().__init__(
            client_id=client_id,
            client_credential=client_credential,
            tenant_id=tenant_id,
            _cache=cache,
            _cae_cache=cae_cache,
            **kwargs
        )
