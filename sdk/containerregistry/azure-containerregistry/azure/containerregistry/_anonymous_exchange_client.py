# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING, Dict, Any

from ._exchange_client import ExchangeClientAuthenticationPolicy
from ._generated import ContainerRegistry
from ._generated.models._container_registry_enums import TokenGrantType
from ._helpers import _parse_challenge
from ._user_agent import USER_AGENT

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class AnonymousACRExchangeClient(object): # pylint: disable=client-accepts-api-version-keyword
    """Class for handling oauth authentication requests

    :param endpoint: Azure Container Registry endpoint
    :type endpoint: str
    :param credential: Credential which provides tokens to authenticate requests
    :type credential: ~azure.core.credentials.TokenCredential
    """

    def __init__(self, endpoint, **kwargs):  # pylint: disable=missing-client-constructor-parameter-credential
        # type: (str, Dict[str, Any]) -> None
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._client = ContainerRegistry(
            credential=None,
            url=endpoint,
            sdk_moniker=USER_AGENT,
            authentication_policy=ExchangeClientAuthenticationPolicy(),
            **kwargs
        )

    def get_acr_access_token(self, challenge, **kwargs):
        # type: (str, Dict[str, Any]) -> str
        parsed_challenge = _parse_challenge(challenge)
        parsed_challenge["grant_type"] = TokenGrantType.PASSWORD
        return self.exchange_refresh_token_for_access_token(
            None,
            service=parsed_challenge["service"],
            scope=parsed_challenge["scope"],
            grant_type=TokenGrantType.PASSWORD,
            **kwargs
        )

    def exchange_refresh_token_for_access_token(
        self, refresh_token=None, service=None, scope=None, grant_type=TokenGrantType.PASSWORD, **kwargs
    ):
        # type: (str, str, str, str, Dict[str, Any]) -> str
        access_token = self._client.authentication.exchange_acr_refresh_token_for_acr_access_token(
            service=service, scope=scope, refresh_token=refresh_token, grant_type=grant_type, **kwargs
        )
        return access_token.access_token

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
