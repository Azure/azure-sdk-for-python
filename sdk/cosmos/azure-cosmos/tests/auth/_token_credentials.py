# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Token-credential builders for the auth test lane.

Provides a sync and an async token credential so the tests can sign in with a
token instead of the account key. By default both build a token the emulator
accepts from ACCOUNT_KEY, so the lane runs anywhere the account key is set. If
COSMOS_AAD_TENANT_ID / COSMOS_AAD_CLIENT_ID / COSMOS_AAD_CLIENT_SECRET are set,
the builders return a real azure-identity credential instead.
"""
from __future__ import annotations

import base64
import json
import os
import time

import pytest
from azure.core.credentials import AccessToken
from azure.identity import ClientSecretCredential
from azure.identity.aio import ClientSecretCredential as AsyncClientSecretCredential

ENV_KEY = "ACCOUNT_KEY"
# Set all three to run against a real Entra tenant instead of the emulator.
_AAD_ENV = ("COSMOS_AAD_TENANT_ID", "COSMOS_AAD_CLIENT_ID", "COSMOS_AAD_CLIENT_SECRET")


def have_real_aad() -> bool:
    """True when all three Entra env vars are set."""
    return all(os.environ.get(v) for v in _AAD_ENV)


def _is_emulator_host() -> bool:
    """True when ACCOUNT_HOST points at the local emulator."""
    host = os.environ.get("ACCOUNT_HOST", "")
    return "localhost" in host or "127.0.0.1" in host


def token_lane_enabled() -> bool:
    """True only where a token can actually sign in: the emulator (the token
    built from the account key is accepted only there) or a real Entra tenant.
    A live account that only takes the account key would fail, so skip it there.
    """
    return _is_emulator_host() or have_real_aad()


def skip_unless_token_auth():
    """pytest mark: skip unless the emulator or a real Entra tenant is set up."""
    return pytest.mark.skipif(
        not token_lane_enabled(),
        reason="Token lane needs the emulator (ACCOUNT_HOST=localhost) "
               "or COSMOS_AAD_TENANT_ID/CLIENT_ID/CLIENT_SECRET set.",
    )


def _mint_emulator_token(master_key: str) -> AccessToken:
    """Build a token the emulator accepts from the account key."""
    header = ('{"typ":"JWT","alg":"RS256","x5t":"CosmosEmulatorPrimaryMaster",'
              '"kid":"CosmosEmulatorPrimaryMaster"}')
    claim = {"aud": "https://localhost.localhost",
             "iss": "https://sts.fake-issuer.net/7b1999a1-dfd7-440e-8204-00170979b984",
             "iat": int(time.time()), "nbf": int(time.time()), "exp": int(time.time() + 7200),
             "appid": "localhost", "appidacr": "1", "idp": "https://localhost:8081/",
             "oid": "96313034-4739-43cb-93cd-74193adbe5b6", "sub": "localhost",
             "tid": "EmulatorFederation", "ver": "1.0", "scp": "user_impersonation"}

    def b64(raw: bytes) -> str:
        return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")

    token = "{}.{}.{}".format(
        b64(header.encode()), b64(json.dumps(claim).replace(" ", "").encode()),
        b64(master_key.encode()),
    )
    return AccessToken(token, int(time.time() + 7200))


class SyncTokenCredential:
    """A token credential with a synchronous get_token."""

    def get_token(self, *scopes, **kwargs) -> AccessToken:  # noqa: D401
        return _mint_emulator_token(os.environ[ENV_KEY])


class AsyncTokenCredential:
    """A token credential with an async get_token. The client runs it on a
    background loop to fetch the token."""

    async def get_token(self, *scopes, **kwargs) -> AccessToken:  # noqa: D401
        return _mint_emulator_token(os.environ[ENV_KEY])


def make_sync_token_credential():
    """Sync token credential: real Entra if configured, else the emulator one."""
    if have_real_aad():
        return ClientSecretCredential(
            os.environ["COSMOS_AAD_TENANT_ID"], os.environ["COSMOS_AAD_CLIENT_ID"],
            os.environ["COSMOS_AAD_CLIENT_SECRET"],
        )
    return SyncTokenCredential()


def make_async_token_credential():
    """Async token credential: real Entra if configured, else the emulator one."""
    if have_real_aad():
        return AsyncClientSecretCredential(
            os.environ["COSMOS_AAD_TENANT_ID"], os.environ["COSMOS_AAD_CLIENT_ID"],
            os.environ["COSMOS_AAD_CLIENT_SECRET"],
        )
    return AsyncTokenCredential()


