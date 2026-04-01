# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from devtools_testutils.aio import recorded_by_proxy_async

from testpreparer import PlaywrightPreparer
from testpreparer_async import PlaywrightClientTestBaseAsync


class TestPlaywrightAccessTokensOperationsAsync(PlaywrightClientTestBaseAsync):
    @PlaywrightPreparer()
    @recorded_by_proxy_async
    async def test_access_tokens_create_or_replace(self, playwright_endpoint, playwright_workspace_id, **kwargs):
        variables = kwargs.pop("variables", {})
        token_id = variables.setdefault("token_id", str(uuid.uuid4()))
        suffix = variables.setdefault("suffix", uuid.uuid4().hex[:4])
        expiry = variables.setdefault(
            "expiry", (datetime.now(timezone.utc) + timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

        client = self.create_async_client(endpoint=playwright_endpoint)
        response = await client.access_tokens.create_or_replace(
            workspace_id=playwright_workspace_id,
            access_token_id=token_id,
            resource={
                "name": f"tk-c-{suffix}",
                "expiryAt": expiry,
            },
        )

        assert response is not None
        assert response["name"] == f"tk-c-{suffix}"
        assert "id" in response
        assert "state" in response
        assert "createdAt" in response
        assert "expiryAt" in response
        return variables

    @PlaywrightPreparer()
    @recorded_by_proxy_async
    async def test_access_tokens_get(self, playwright_endpoint, playwright_workspace_id, **kwargs):
        variables = kwargs.pop("variables", {})
        token_id = variables.setdefault("token_id", str(uuid.uuid4()))
        suffix = variables.setdefault("suffix", uuid.uuid4().hex[:4])
        expiry = variables.setdefault(
            "expiry", (datetime.now(timezone.utc) + timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

        client = self.create_async_client(endpoint=playwright_endpoint)
        await client.access_tokens.create_or_replace(
            workspace_id=playwright_workspace_id,
            access_token_id=token_id,
            resource={
                "name": f"tk-g-{suffix}",
                "expiryAt": expiry,
            },
        )

        response = await client.access_tokens.get(
            workspace_id=playwright_workspace_id,
            access_token_id=token_id,
        )

        assert response is not None
        assert response["name"] == f"tk-g-{suffix}"
        assert response["id"] is not None
        return variables

    @PlaywrightPreparer()
    @recorded_by_proxy_async
    async def test_access_tokens_delete(self, playwright_endpoint, playwright_workspace_id, **kwargs):
        variables = kwargs.pop("variables", {})
        token_id = variables.setdefault("token_id", str(uuid.uuid4()))
        suffix = variables.setdefault("suffix", uuid.uuid4().hex[:4])
        expiry = variables.setdefault(
            "expiry", (datetime.now(timezone.utc) + timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

        client = self.create_async_client(endpoint=playwright_endpoint)
        await client.access_tokens.create_or_replace(
            workspace_id=playwright_workspace_id,
            access_token_id=token_id,
            resource={
                "name": f"tk-d-{suffix}",
                "expiryAt": expiry,
            },
        )

        response = await client.access_tokens.delete(
            workspace_id=playwright_workspace_id,
            access_token_id=token_id,
        )
        assert response is None
        return variables

    @PlaywrightPreparer()
    @recorded_by_proxy_async
    async def test_access_tokens_list(self, playwright_endpoint, playwright_workspace_id):
        client = self.create_async_client(endpoint=playwright_endpoint)
        response = client.access_tokens.list(
            workspace_id=playwright_workspace_id,
        )
        result = [r async for r in response]
        assert isinstance(result, list)
