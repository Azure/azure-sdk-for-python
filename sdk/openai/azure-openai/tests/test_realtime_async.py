# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import openai
import httpx
from devtools_testutils import AzureRecordedTestCase, get_credential
from azure.identity.aio import get_bearer_token_provider
from conftest import (
    ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT,
    ENV_AZURE_OPENAI_SWEDENCENTRAL_KEY,
    GPT_4_AZURE,
    GPT_4_OPENAI,
    configure_async,
)

async_client = openai.AsyncOpenAI(
    base_url=os.getenv(ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT).strip("/") + "/openai",
    bearer_token_provider=get_bearer_token_provider(get_credential(), "https://cognitiveservices.azure.com/.default"),
)

@pytest.mark.live_test_only
class TestRealtimeAsync(AzureRecordedTestCase):

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, "2024-10-01-preview")]
    )
    async def test_realtime_text(self, client_async, api_type, api_version, **kwargs):
        async with async_client.beta.realtime.connect(
            extra_query={"api-version": "2024-10-01-preview", "deployment": "gpt-4o-mini-realtime-preview-1217"}, **kwargs,
        ) as connection:
            await connection.session.update(session={"modalities": ["text"]})
            await connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Say hello!"}],
                }
            )
            await connection.response.create()
            async for event in connection:
                if event.type == "response.text.delta":
                    assert event.delta
                elif event.type == "response.text.done":
                    assert event.text
                elif event.type == "response.done":
                    break

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, "2024-10-01-preview")],
    )
    async def test_realtime_text_api_key(self, client_async, api_type, api_version, **kwargs):

        async_client = openai.AsyncOpenAI(
            base_url=os.getenv(ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT).strip("/") + "/openai",
            api_key=os.environ[ENV_AZURE_OPENAI_SWEDENCENTRAL_KEY],
        )
        async with async_client.beta.realtime.connect(
            extra_query={"api-version": "2024-10-01-preview", "deployment": "gpt-4o-mini-realtime-preview-1217"}, **kwargs,
        ) as connection:
            await connection.session.update(session={"modalities": ["text"]})
            await connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Say hello!"}],
                }
            )
            await connection.response.create()
            async for event in connection:
                if event.type == "response.text.delta":
                    assert event.delta
                elif event.type == "response.text.done":
                    assert event.text
                elif event.type == "response.done":
                    break

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, "2024-10-01-preview")],
    )
    async def test_realtime_text_ad_token(self, client_async, api_type, api_version, **kwargs):
        credential = get_credential(is_async=True)
        access_token = await credential.get_token("https://cognitiveservices.azure.com/.default")
        client_async = openai.AsyncAzureOpenAI(
            azure_endpoint=os.environ[ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT],
            azure_ad_token=access_token.token,
            api_version=api_version,
        )
        async with client_async.beta.realtime.connect(
            **kwargs
        ) as connection:
            await connection.session.update(session={"modalities": ["text"]})
            await connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Say hello!"}],
                }
            )
            await connection.response.create()
            async for event in connection:
                if event.type == "response.text.delta":
                    assert event.delta
                elif event.type == "response.text.done":
                    assert event.text
                elif event.type == "response.done":
                    break

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, "2024-10-01-preview")],
    )
    async def test_realtime_text_deployment_name(self, client_async, api_type, api_version, **kwargs):
        client_async = openai.AsyncAzureOpenAI(
            azure_endpoint=os.environ[ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT],
            api_key=os.environ[ENV_AZURE_OPENAI_SWEDENCENTRAL_KEY],
            api_version=api_version,
            azure_deployment="gpt-4o-mini-realtime-preview-1217",
        )
        async with client_async.beta.realtime.connect(
            model="invalid"
        ) as connection:
            await connection.session.update(session={"modalities": ["text"]})
            await connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Say hello!"}],
                }
            )
            await connection.response.create()
            async for event in connection:
                if event.type == "response.text.delta":
                    assert event.delta
                elif event.type == "response.text.done":
                    assert event.text
                elif event.type == "response.done":
                    break

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, "2024-10-01-preview")],
    )
    async def test_realtime_text_websocket_base_url(self, client_async, api_type, api_version, **kwargs):
        
        async_client = openai.AsyncOpenAI(
            base_url="fakebaseurl",
            websocket_base_url=httpx.URL(os.getenv(ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT) + "/openai/").copy_with(scheme="wss"),
            bearer_token_provider=get_bearer_token_provider(get_credential(), "https://cognitiveservices.azure.com/.default"),
        )

        async with async_client.beta.realtime.connect(
            extra_query={"api-version": "2024-10-01-preview", "deployment": "gpt-4o-mini-realtime-preview-1217"}, **kwargs,
        ) as connection:
            await connection.session.update(session={"modalities": ["text"]})
            await connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Say hello!"}],
                }
            )
            await connection.response.create()
            async for event in connection:
                if event.type == "response.text.delta":
                    assert event.delta
                elif event.type == "response.text.done":
                    assert event.text
                elif event.type == "response.done":
                    break
