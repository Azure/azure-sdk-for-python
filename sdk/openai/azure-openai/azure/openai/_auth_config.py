# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
from typing import Optional, Union
import time
import logging
import requests
import openai
from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential


log = logging.getLogger(__name__)


class CredentialRefresh:

    def __init__(self, credential: Union[TokenCredential, str], *scopes: str) -> None:
        self.credential = credential
        self.scopes = scopes
        self.cached_token: Optional[str] = None

    def __call__(self, req):
        if isinstance(self.credential, str):
            req.headers["api-key"] = openai.api_key
            return req
        if not self.cached_token or self.cached_token.expires_on - time.time() < 300:
            self.cached_token = self.credential.get_token(*self.scopes)
        req.headers["Authorization"] = f"Bearer {self.cached_token.token}"
        return req


def login():

    session = requests.Session()  # match openai config?

    # API version is not configured by env var in openai yet
    openai.api_version = os.getenv("OPENAI_API_VERSION", "2022-12-01")

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key in["azuread", "azure_ad"]:
        openai.api_type = "azuread"
        openai.api_key = "API_KEY"
        credential = DefaultAzureCredential()
        scopes = ["https://cognitiveservices.azure.com/.default"]
        session.auth = CredentialRefresh(credential, *scopes)
    else:
        session.auth = CredentialRefresh(api_key)

    # probably should not set session if using OAI...
    openai.requestssession = session
    return session
