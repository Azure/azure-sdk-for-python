# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import openai
from devtools_testutils import AzureRecordedTestCase, get_credential
from conftest import (
    ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT,
    ENV_AZURE_OPENAI_SWEDENCENTRAL_KEY,
    GPT_4_AZURE,
    GPT_4_OPENAI,
    configure_async,
    PREVIEW,
)


@pytest.mark.live_test_only
class TestRealtimeAsync(AzureRecordedTestCase):

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")],
    )
    async def test_realtime_text(self, client_async, api_type, api_version, **kwargs):
        async with client_async.beta.realtime.connect(
            **kwargs,
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
        [(GPT_4_AZURE, PREVIEW)],
    )
    async def test_realtime_text_api_key(self, client_async, api_type, api_version, **kwargs):
        client_async = openai.AsyncAzureOpenAI(
            azure_endpoint=os.environ[ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT],
            api_key=os.environ[ENV_AZURE_OPENAI_SWEDENCENTRAL_KEY],
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
        [(GPT_4_AZURE, PREVIEW)],
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
