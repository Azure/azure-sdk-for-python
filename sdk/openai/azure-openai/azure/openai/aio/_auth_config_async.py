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
from .._auth_config import get_scopes


log = logging.getLogger(__name__)


class AsyncCredentialRefresh(aiohttp.ClientRequest):
    props: Dict[str, Any]  # this is not ideal...

    async def _refresh_credential(self):
        if isinstance(self.props["credential"], str):
            if openai.api_type == "azure":
                self.headers["api-key"] = openai.api_key
            elif openai.api_type in ["azuread", "azure_ad", "openai", "open_ai"]:
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

    if hasattr(api_key, "get_token"):
        openai.api_type = "azuread"
        openai.api_key = "API_KEY"
        request_class.props = {"credential": api_key, "scopes": get_scopes(scopes), "cached_token": None, "lock": asyncio.Lock()}
    elif openai.api_type in ["azuread", "azure_ad"] and openai.api_key is None:
        openai.api_key = "API_KEY"
        credential = DefaultAzureCredential()
        request_class.props = {"credential": credential, "scopes": get_scopes(scopes), "cached_token": None, "lock": asyncio.Lock()}
    else:
        request_class.props = {"credential": openai.api_key}

    # probably should not set session if using OAI...
    session = aiohttp.ClientSession(request_class=request_class)
    openai.aiosession.set(session)
    return session
