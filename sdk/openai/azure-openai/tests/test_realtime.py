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
    configure,
    PREVIEW,
)


@pytest.mark.live_test_only
class TestRealtime(AzureRecordedTestCase):

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")],
    )
    def test_realtime_text(self, client, api_type, api_version, **kwargs):
        with client.beta.realtime.connect(
            **kwargs,
        ) as connection:
            connection.session.update(session={"modalities": ["text"]})
            connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Say hello!"}],
                }
            )
            connection.response.create()
            for event in connection:
                if event.type == "response.text.delta":
                    assert event.delta
                elif event.type == "response.text.done":
                    assert event.text
                elif event.type == "response.done":
                    break

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW)],
    )
    def test_realtime_text_api_key(self, client, api_type, api_version, **kwargs):
        client = openai.AzureOpenAI(
            azure_endpoint=os.environ[ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT],
            api_key=os.environ[ENV_AZURE_OPENAI_SWEDENCENTRAL_KEY],
            api_version=api_version,
        )
        with client.beta.realtime.connect(
            **kwargs
        ) as connection:
            connection.session.update(session={"modalities": ["text"]})
            connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Say hello!"}],
                }
            )
            connection.response.create()
            for event in connection:
                if event.type == "response.text.delta":
                    assert event.delta
                elif event.type == "response.text.done":
                    assert event.text
                elif event.type == "response.done":
                    break

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW)],
    )
    def test_realtime_text_ad_token(self, client, api_type, api_version, **kwargs):
        client = openai.AzureOpenAI(
            azure_endpoint=os.environ[ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT],
            azure_ad_token=get_credential().get_token("https://cognitiveservices.azure.com/.default").token,
            api_version=api_version,
        )
        with client.beta.realtime.connect(
            **kwargs
        ) as connection:
            connection.session.update(session={"modalities": ["text"]})
            connection.conversation.item.create(
                item={
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Say hello!"}],
                }
            )
            connection.response.create()
            for event in connection:
                if event.type == "response.text.delta":
                    assert event.delta
                elif event.type == "response.text.done":
                    assert event.text
                elif event.type == "response.done":
                    break
