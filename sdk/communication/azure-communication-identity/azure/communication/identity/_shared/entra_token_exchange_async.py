# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any
from azure.core.credentials import AccessToken
import aiohttp
import asyncio

class EntraTokenExchangeClientAsync(object):
    """Async client for exchanging a customer-provided Entra ID token for a new user access token via the TeamsExtension token exchange endpoint.

    :param str endpoint: The endpoint URL for the token exchange service.
    :param str customer_token: The Entra ID token provided by the customer, used for authentication.
    """

    def __init__(self, endpoint: str, customer_token: str, **kwargs: Any) -> None:
        if not isinstance(endpoint, str) or not endpoint:
            raise ValueError("Endpoint must be a non-empty string.")
        if not isinstance(customer_token, str) or not customer_token:
            raise ValueError("Customer token must be a non-empty string.")
        self._endpoint = endpoint
        self._customer_token = customer_token
        self._lock = asyncio.Lock()  # Async lock for thread safety

    async def exchange_token(self, **kwargs: Any) -> AccessToken:
        """Asynchronously exchanges the customer-provided Entra ID token for a new user access token.

        :return: An AccessToken instance containing the new user access token and its expiration.
        :rtype: ~azure.core.credentials.AccessToken
        """
        async with self._lock:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._endpoint,
                    headers={
                        "Authorization": f"Bearer {self._customer_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    json=kwargs.get("payload", {}),
                    timeout=30,
                ) as response:
                    response.raise_for_status()
                    token_data = await response.json()
                    return AccessToken(token_data["accessToken"]["token"], token_data["accessToken"]["expiresOn"])