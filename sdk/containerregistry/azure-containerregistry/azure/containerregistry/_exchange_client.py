# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os

from azure.core.pipeline.policies import SansIOHTTPPolicy

from ._generated import ContainerRegistry
from ._user_agent import USER_AGENT


class ExchangeClientAuthenticationPolicy(SansIOHTTPPolicy):
    """Authentication policy for exchange client that does not modify the request"""

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        pass

    def on_response(self, request, response):
        # type: (PipelineRequest, PipelineResponse) -> None
        pass


class ACRExchangeClient(object):
    """Class for handling oauth authentication requests

    :param endpoint: Azure Container Registry endpoint
    :type endpoint: str
    :param credential: AAD Token for authenticating requests with Azure
    :type credential: :class:`azure.identity.DefaultTokenCredential`

    """

    def __init__(self, endpoint, credential, **kwargs):
        if not endpoint.startswith("https://"):
            endpoint = "https://" + endpoint
        self._credential_scopes = "https://management.core.windows.net/.default"
        self._client = ContainerRegistry(
            credential=credential,
            url=endpoint,
            sdk_moniker=USER_AGENT,
            authentication_policy=ExchangeClientAuthenticationPolicy(),
            credential_scopes=kwargs.pop("credential_scopes", self._credential_scopes),
            **kwargs
        )
        self._credential = credential

    def get_refresh_token(self, service, tenant):
        return self._client.authentication.exchange_aad_token_for_acr_refresh_token(
            service=service,
            tenant=os.environ["AZURE_TENANT_ID"],
            access_token=self._credential.get_token(self._credential_scopes)
        )

    def get_acr_access_token(self, service, scope, refresh_token):
        return self.authentication.access_tokens.get(service, scope, refresh_token)

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    def close(self):
        # type: () -> None
        """Close sockets opened by the client.
        Calling this method is unnecessary when using the client as a context manager.
        """
        self._client.close()
