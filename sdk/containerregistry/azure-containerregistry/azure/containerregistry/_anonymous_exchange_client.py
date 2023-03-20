# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Optional, Union, overload
from azure.core.credentials import TokenCredential
from ._exchange_client import ExchangeClientAuthenticationPolicy
from ._generated import ContainerRegistry
from ._generated.models import TokenGrantType
from ._helpers import _parse_challenge
from ._user_agent import USER_AGENT


class AnonymousAccessCredential(TokenCredential):
    @overload
    def get_token(
        self, *scopes: str, claims: Optional[str] = None, tenant_id: Optional[str] = None, **kwargs
    ) -> None:
        raise ValueError("This credential cannot be used to obtain access tokens.")


class AnonymousACRExchangeClient(object):
    """Class for handling oauth authentication requests

    :param endpoint: Azure Container Registry endpoint
    :type endpoint: str
    :keyword api_version: API Version. The default value is "2021-07-01". Note that overriding this default value
     may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint, **kwargs):  # pylint: disable=missing-client-constructor-parameter-credential
        # type: (str, Any) -> None
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._client = ContainerRegistry(
            credential=AnonymousAccessCredential(),
            url=endpoint,
            sdk_moniker=USER_AGENT,
            authentication_policy=ExchangeClientAuthenticationPolicy(),
            **kwargs
        )

    def get_acr_access_token(self, challenge, **kwargs):
        # type: (str, Any) -> Optional[str]
        parsed_challenge = _parse_challenge(challenge)
        return self.exchange_refresh_token_for_access_token(
            "",
            service=parsed_challenge["service"],
            scope=parsed_challenge["scope"],
            grant_type=TokenGrantType.PASSWORD,
            **kwargs
        )

    def exchange_refresh_token_for_access_token(self, refresh_token, service, scope, grant_type, **kwargs):
        # type: (str, str, str, Union[str, TokenGrantType], Any) -> Optional[str]
        access_token = self._client.authentication.exchange_acr_refresh_token_for_acr_access_token( # type: ignore
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
