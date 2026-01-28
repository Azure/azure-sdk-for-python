# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import pytest
import httpx
from typing import Any, Dict, Optional
from openai import AsyncOpenAI
from azure.core.credentials import AccessToken
from azure.core.credentials_async import AsyncTokenCredential
from azure.ai.projects.aio import AIProjectClient
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport

BASE_OPENAI_UA = AsyncOpenAI(api_key="dummy").user_agent


class DummyAsyncTokenCredential(AsyncTokenCredential):
    async def get_token(self, *scopes: str, **kwargs: Any):  # type: ignore[override]
        return AccessToken("token", 0)


def _build_dummy_client(
    project_user_agent: Optional[str],
    default_headers: Optional[Dict[str, str]],
):
    project_client = AIProjectClient(
        "https://example.com/api/projects/test",
        DummyAsyncTokenCredential(),
        user_agent=project_user_agent,
    )
    kwargs: Dict[str, Any] = {"default_headers": default_headers}
    return project_client.get_openai_client(**kwargs)


class TestResponsesAsync(TestBase):

    # To run this test:
    # pytest tests\responses\test_responses_async.py::TestResponsesAsync::test_responses_async -s
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.HTTPX)
    async def test_responses_async(self, **kwargs):

        model = kwargs.get("azure_ai_model_deployment_name")

        client = self.create_async_client(operation_group="agents", **kwargs).get_openai_client()

        async with client:

            response1 = await client.responses.create(
                model=model,
                input="How many feet in a mile?",
            )
            print(f"Response id: {response1.id}, output text: {response1.output_text}")
            assert "5280" in response1.output_text or "5,280" in response1.output_text

            response2 = await client.responses.create(
                model=model, input="And how many meters?", previous_response_id=response1.id
            )
            print(f"Response id: {response2.id}, output text: {response2.output_text}")
            assert "1609" in response2.output_text or "1,609" in response2.output_text

    @pytest.mark.parametrize(
        "project_ua,openai_default_header,expected_ua",
        [
            # 1) No user_agent anywhere
            (
                None,
                None,
                f"AIProjectClient {BASE_OPENAI_UA}",
            ),
            # 2) user_agent at project client only
            (
                "custom-client-ua",
                None,
                f"custom-client-ua-AIProjectClient {BASE_OPENAI_UA}",
            ),
            # 3) user_agent at openai client only
            (
                None,
                {"User-Agent": "custom-openai-ua"},
                "custom-openai-ua",
            ),
            # 4) user_agent at both clients only
            (
                "custom-client-ua",
                {"User-Agent": "custom-openai-ua"},
                "custom-openai-ua",
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_user_agent_patching_via_response_create(self, project_ua, openai_default_header, expected_ua):
        client = _build_dummy_client(project_ua, openai_default_header)

        calls = []

        async def fake_send(request: httpx.Request, *args: Any, **kwargs: Any):
            # Capture headers that would be sent over the wire.
            calls.append(dict(request.headers))
            return httpx.Response(
                200,
                request=request,
                json={
                    "id": "resp_123",
                    "object": "response",
                    "model": kwargs.get("model", ""),
                    "status": "ok",
                    "output": "",
                },
            )

        # Monkeypatch the underlying httpx client used by the OpenAI client instance.
        client._client.send = fake_send  # type: ignore[attr-defined]

        # Act through the actual call surface
        await client.responses.create(model="gpt-4o")

        # Assert
        assert calls, "Expected a responses.create call to be captured"
        headers_used = {k.lower(): v for k, v in calls[0].items()}

        assert headers_used["user-agent"] == expected_ua
