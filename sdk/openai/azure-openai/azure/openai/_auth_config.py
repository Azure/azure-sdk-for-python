# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
from typing import Optional, Union, List
import time
import logging
import requests
import openai
from typing_extensions import Literal
from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential


log = logging.getLogger(__name__)


class CredentialRefresh:

    def __init__(self, credential: Union[TokenCredential, str], *, scopes: Optional[List[str]] = None) -> None:
        self.credential = credential
        self.scopes = scopes
        self.cached_token: Optional[str] = None

    def __call__(self, req):
        if isinstance(self.credential, str):
            if openai.api_type in ["azure", "openai", "open_ai"]:
                req.headers["api-key"] = openai.api_key
            elif openai.api_type in ["azuread", "azure_ad"]:
                req.headers["Authorization"] = f"Bearer {openai.api_key}"
            return req
        if not self.cached_token or self.cached_token.expires_on - time.time() < 300:
            self.cached_token = self.credential.get_token(*self.scopes)
        req.headers["Authorization"] = f"Bearer {self.cached_token.token}"
        return req


def get_scopes(scopes: Optional[Union[str, List[str]]]) -> List[str]:
    scopes = [scopes] if isinstance(scopes, str) else scopes
    if scopes is None:
        scopes = ["https://cognitiveservices.azure.com/.default"]
    return scopes


def login(
    *,
    api_key: Optional[Union[str, TokenCredential]] = None,
    api_key_path: Optional[str] = None,
    api_base: Optional[str] = None,
    api_type: Optional[Literal["azuread", "azure_ad", "azure", "openai", "open_ai"]] = None,
    api_version: Optional[str] = None,
    organization: Optional[str] = None,
    scopes: Optional[Union[str, List[str]]] = None,
):

    session = requests.Session()  # match openai config?

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

    # API version is not configured by env var in openai yet
    # PR: https://github.com/openai/openai-python/pull/438
    openai.api_version = os.environ.get(
        "OPENAI_API_VERSION",
        ("2023-03-15-preview" if api_type in ("azure", "azure_ad", "azuread") else None),
    )

    if api_version:
        # should we default api version?
        openai.api_version = api_version

    if hasattr(api_key, "get_token"):
        openai.api_type = "azuread"
        openai.api_key = "API_KEY"
        session.auth = CredentialRefresh(api_key, scopes=get_scopes(scopes))
    elif openai.api_type in ["azuread", "azure_ad"] and openai.api_key is None:
        openai.api_key = "API_KEY"
        credential = DefaultAzureCredential()
        session.auth = CredentialRefresh(credential, scopes=get_scopes(scopes))
    else:
        # should we assume api_type azure here? or take openai default? what if it's a token string?
        session.auth = CredentialRefresh(openai.api_key)

    # probably should not set session if using OAI...
    # should we create single session or provide sesssion factory?
    openai.requestssession = session
    return session
