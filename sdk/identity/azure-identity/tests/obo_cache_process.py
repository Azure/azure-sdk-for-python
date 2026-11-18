# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Subprocess worker for the async OBO persistent cache regression test."""

import asyncio
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from azure.identity import TokenCachePersistenceOptions
from azure.identity.aio import OnBehalfOfCredential
from msal_extensions import FilePersistence

from helpers import build_aad_response, mock_response
from helpers_async import AsyncMockTransport


async def main():
    settings = json.load(sys.stdin)
    directory = Path(settings["directory"])
    assertion = settings["assertion"]
    requests = []

    async def send(request, **kwargs):
        assert request.body["client_id"] == "client-id"
        requests.append(request.body["grant_type"])
        if settings["mode"] == "write":
            assert request.body["assertion"] == assertion
            assert "refresh_token" not in request.body
            (directory / (assertion + ".ready")).touch()

            async def wait_for_writers():
                while not all((directory / (user + ".ready")).exists() for user in ("a", "b")):
                    await asyncio.sleep(0.01)

            await asyncio.wait_for(wait_for_writers(), timeout=10)
            return mock_response(
                json_payload=build_aad_response(
                    access_token="access-" + assertion,
                    refresh_token="refresh-" + assertion,
                    expires_in=0 if settings["expired"] else 3600,
                    uid="same-user",
                    utid="home-tenant",
                )
            )
        assert settings["mode"] == "refresh", "a new process unexpectedly contacted the token endpoint"
        assert request.body["refresh_token"] == "refresh-" + assertion
        assert "assertion" not in request.body
        return mock_response(
            json_payload=build_aad_response(access_token="refreshed-" + assertion, refresh_token="rotated-" + assertion)
        )

    def persistence(**kwargs):
        return FilePersistence(str(directory / kwargs["cache_name"]))

    with patch("azure.identity._persistent_cache._get_persistence", persistence):
        async with OnBehalfOfCredential(
            "tenant-id",
            "client-id",
            client_secret="secret",
            user_assertion=assertion,
            cache_persistence_options=TokenCachePersistenceOptions(name="obo-process-test"),
            transport=AsyncMockTransport(send=send),
        ) as credential:
            token = await credential.get_token("scope", enable_cae=settings["enable_cae"])
            refresh_tokens = credential._client.get_cached_refresh_tokens(["scope"], enable_cae=settings["enable_cae"])
            print(json.dumps({"token": token.token, "requests": requests, "refresh_tokens": refresh_tokens}))


if __name__ == "__main__":
    asyncio.run(main())
