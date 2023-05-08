# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
from typing import Optional, Union, List, Dict, Any
import time
import logging
import asyncio
import openai
import aiohttp
from typing_extensions import Literal
from azure.core.credentials_async import AsyncTokenCredential
from azure.identity.aio import DefaultAzureCredential


log = logging.getLogger(__name__)


class AsyncCredentialRefresh(aiohttp.ClientRequest):
    props: Dict[str, Any]  # this is not ideal...

    async def _refresh_credential(self):
        if isinstance(self.props["credential"], str):
            if openai.api_type in ["azure", "openai", "open_ai"]:
                self.headers["api-key"] = openai.api_key
            elif openai.api_type in ["azuread", "azure_ad"]:
                self.headers["Authorization"] = f"Bearer {openai.api_key}"
        elif self.props.get("cached_token") is None or self.props.get("cached_token").expires_on - time.time() < 300:
            async with self.props.get("lock"):
                if self.props.get("cached_token") is None or self.props.get("cached_token").expires_on - time.time() < 300:
                    self.props["cached_token"] = await self.props["credential"].get_token(*self.props.get("scopes"))
            self.headers["Authorization"] = "Bearer " + self.props["cached_token"].token

    async def send(self, conn: "Connection") -> "aiohttp.ClientResponse":
        await self._refresh_credential()
        return await super().send(conn)


def login(
    *,
    api_key: Optional[Union[str, AsyncTokenCredential]] = None,
    api_key_path: Optional[str] = None,
    api_base: Optional[str] = None,
    api_type: Optional[Literal["azuread", "azure_ad", "azure", "openai", "open_ai"]] = None,
    api_version: Optional[str] = None,
    organization: Optional[str] = None,
    scopes: Optional[Union[str, List[str]]] = None,
):

    request_class = AsyncCredentialRefresh

    if api_base:
        openai.api_base = api_base

    if api_key:
        openai.api_key = api_key

    if api_key_path:
        openai.api_key_path = api_key_path

    if organization:
        openai.organization = organization

    if api_type:
        openai.api_type = api_type

    if api_version:
        openai.api_version = api_version

    if openai.api_version is None:
        # API version is not configured by env var in openai yet
        # PR: https://github.com/openai/openai-python/pull/438
        openai.api_version = os.getenv("OPENAI_API_VERSION", "2022-12-01")

    if hasattr(api_key, "get_token"):
        openai.api_type = "azuread"
        openai.api_key = "API_KEY"
        scopes = [scopes] if isinstance(scopes, str) else scopes
        if scopes is None:
            scopes = ["https://cognitiveservices.azure.com/.default"]
        request_class.props = {"credential": api_key, "scopes": scopes, "cached_token": None, "lock": asyncio.Lock()}
    elif openai.api_type in ["azuread", "azure_ad"] and openai.api_key is None:
        openai.api_key = "API_KEY"
        credential = DefaultAzureCredential()
        scopes = [scopes] if isinstance(scopes, str) else scopes
        if scopes is None:
            scopes = ["https://cognitiveservices.azure.com/.default"]
        request_class.props = {"credential": credential, "scopes": scopes, "cached_token": None, "lock": asyncio.Lock()}
    else:
        if openai.api_type is None:
            raise ValueError("Must pass api_type or set OPENAI_API_TYPE environment variable with api_key.")
        request_class.props = {"credential": api_key}

    # probably should not set session if using OAI...
    session = aiohttp.ClientSession(request_class=request_class)
    openai.aiosession.set(session)
    return session
