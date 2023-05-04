# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import typing
import time
import logging
import asyncio
import openai
import aiohttp
from azure.identity.aio import DefaultAzureCredential


log = logging.getLogger(__name__)


class AsyncCredentialRefresh(aiohttp.ClientRequest):
    props: typing.Dict[str, typing.Any]  # this is not ideal...

    async def _refresh_credential(self):
        if isinstance(self.props["credential"], str):
            self.headers["api-key"] = openai.api_key
            return
        if self.props.get("cached_token") is None or self.props.get("cached_token").expires_on - time.time() < 300:
            async with self.props.get("lock"):
                if self.props.get("cached_token") is None or self.props.get("cached_token").expires_on - time.time() < 300:
                    self.props["cached_token"] = await self.props["credential"].get_token(*self.props.get("scopes"))
            self.headers["Authorization"] = "Bearer " + self.props["cached_token"].token

    async def send(self, conn: "Connection") -> "aiohttp.ClientResponse":
        await self._refresh_credential()
        return await super().send(conn)


def login():

    request_class = AsyncCredentialRefresh

    # API version is not configured by env var in openai yet
    openai.api_version = os.getenv("OPENAI_API_VERSION", "2022-12-01")

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key in["azuread", "azure_ad"]:
        openai.api_type = "azuread"
        openai.api_key = "API_KEY"
        credential = DefaultAzureCredential()
        scopes = ["https://cognitiveservices.azure.com/.default"]
        request_class.props = {"credential": credential, "scopes": scopes, "cached_token": None, "lock": asyncio.Lock()}
    else:
        request_class.props = {"credential": api_key}

    # probably should not set session if using OAI...
    session = aiohttp.ClientSession(request_class=request_class)
    openai.aiosession.set(session)
    return session
