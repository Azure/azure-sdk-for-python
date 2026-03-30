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

TOKEN_ID_CREATE = str(uuid.uuid4())
TOKEN_ID_GET = str(uuid.uuid4())
TOKEN_ID_DELETE = str(uuid.uuid4())
TOKEN_EXPIRY = (datetime.now(timezone.utc) + timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%SZ")
_SUFFIX = uuid.uuid4().hex[:4]


class TestPlaywrightAccessTokensOperationsAsync(PlaywrightClientTestBaseAsync):
    @PlaywrightPreparer()
    @recorded_by_proxy_async
    async def test_access_tokens_create_or_replace(self, playwright_endpoint, playwright_workspace_id):
        client = self.create_async_client(endpoint=playwright_endpoint)
        response = await client.access_tokens.create_or_replace(
            workspace_id=playwright_workspace_id,
            access_token_id=TOKEN_ID_CREATE,
            resource={
                "name": f"tk-c-{_SUFFIX}",
                "expiryAt": TOKEN_EXPIRY,
            },
        )

        assert response is not None
        assert response["name"] == f"tk-c-{_SUFFIX}"
        assert "id" in response
        assert "state" in response
        assert "createdAt" in response
        assert "expiryAt" in response

    @PlaywrightPreparer()
    @recorded_by_proxy_async
    async def test_access_tokens_get(self, playwright_endpoint, playwright_workspace_id):
        client = self.create_async_client(endpoint=playwright_endpoint)
        await client.access_tokens.create_or_replace(
            workspace_id=playwright_workspace_id,
            access_token_id=TOKEN_ID_GET,
            resource={
                "name": f"tk-g-{_SUFFIX}",
                "expiryAt": TOKEN_EXPIRY,
            },
        )

        response = await client.access_tokens.get(
            workspace_id=playwright_workspace_id,
            access_token_id=TOKEN_ID_GET,
        )

        assert response is not None
        assert response["name"] == f"tk-g-{_SUFFIX}"
        assert response["id"] is not None

    @PlaywrightPreparer()
    @recorded_by_proxy_async
    async def test_access_tokens_delete(self, playwright_endpoint, playwright_workspace_id):
        client = self.create_async_client(endpoint=playwright_endpoint)
        await client.access_tokens.create_or_replace(
            workspace_id=playwright_workspace_id,
            access_token_id=TOKEN_ID_DELETE,
            resource={
                "name": f"tk-d-{_SUFFIX}",
                "expiryAt": TOKEN_EXPIRY,
            },
        )

        response = await client.access_tokens.delete(
            workspace_id=playwright_workspace_id,
            access_token_id=TOKEN_ID_DELETE,
        )
        assert response is None

    @PlaywrightPreparer()
    @recorded_by_proxy_async
    async def test_access_tokens_list(self, playwright_endpoint, playwright_workspace_id):
        client = self.create_async_client(endpoint=playwright_endpoint)
        response = client.access_tokens.list(
            workspace_id=playwright_workspace_id,
        )
        result = [r async for r in response]
        assert isinstance(result, list)
