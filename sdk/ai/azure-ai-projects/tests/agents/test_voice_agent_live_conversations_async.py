# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async Test Proxy coverage of the same GPT Live REST lifecycle as the sync test."""

import pytest

from azure.ai.projects import models
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import is_live
from devtools_testutils.aio import recorded_by_proxy_async
from test_base import TestBase
from live_conversation_test_base import (
    LiveConversationPreparer,
    add_live_conversation_sanitizers,
    assert_audio_metadata,
    assert_completed_conversation,
    assert_live_status,
    assert_speech_item,
    assert_wav,
    liveConversationServicePreparer,
)


class TestVoiceAgentLiveConversationsAsync(TestBase):
    @liveConversationServicePreparer()
    @LiveConversationPreparer()
    @recorded_by_proxy_async()
    async def test_live_conversation_rest_lifecycle_async(self, live_conversation_fixture, **kwargs):
        await self._test_live_conversation_rest_lifecycle_async(live_conversation_fixture, **kwargs)

    async def _test_live_conversation_rest_lifecycle_async(self, live_conversation_fixture, **kwargs):
        fixture = live_conversation_fixture
        if is_live():
            add_live_conversation_sanitizers(fixture)
        async with self.create_async_client(allow_preview=True, **kwargs) as client:
            conversations = client.beta.voice_agents.live_conversations
            agent_name, conversation_id = fixture.agent_name, fixture.conversation_ids[0]
            listed = [
                value
                async for value in conversations.list(
                    agent_name, limit=1, order="asc", raw_response_hook=assert_live_status(200)
                )
            ]
            assert [value.id for value in listed] == list(fixture.conversation_ids)
            for value in listed:
                assert_completed_conversation(value, value.id)
            detail = await conversations.get(agent_name, conversation_id, raw_response_hook=assert_live_status(200))
            assert_completed_conversation(detail, conversation_id)

            items = [
                item
                async for item in conversations.list_items(
                    agent_name, conversation_id, limit=1, order="asc", raw_response_hook=assert_live_status(200)
                )
            ]
            assert items and len({item.id for item in items}) == len(items)
            assert all(isinstance(item, models.VoiceAgentLiveConversationItem) for item in items)
            speech = [item for item in items if isinstance(item, models.VoiceAgentLiveOutputConversationItem)]
            assert speech, "Stored greeting speech must exercise item audio, not just metadata/list routes"
            for item in speech:
                assert_speech_item(item)
                fetched = await conversations.get_item(
                    agent_name, conversation_id, item.id, raw_response_hook=assert_live_status(200)
                )
                fetched = assert_speech_item(fetched, item.id)
                assert fetched.transcription == item.transcription
                audio = await conversations.get_audio_item(
                    agent_name, conversation_id, item.id, raw_response_hook=assert_live_status(200)
                )
                assert_audio_metadata(audio, conversation_id, item_id=item.id)
                stream = await conversations.download_audio_item(
                    agent_name, conversation_id, item.id, raw_response_hook=assert_live_status(200)
                )
                assert_wav(b"".join([chunk async for chunk in stream]), audio)
            recording = await conversations.get_audio(
                agent_name, conversation_id, raw_response_hook=assert_live_status(200)
            )
            assert_audio_metadata(recording, conversation_id)
            stream = await conversations.download_audio(
                agent_name, conversation_id, raw_response_hook=assert_live_status(200)
            )
            assert_wav(b"".join([chunk async for chunk in stream]), recording)

            await conversations.delete(agent_name, conversation_id, raw_response_hook=assert_live_status(204))
            with pytest.raises(ResourceNotFoundError):
                await conversations.get(agent_name, conversation_id, raw_response_hook=assert_live_status(404))
            with pytest.raises(ResourceNotFoundError):
                await conversations.get_item(
                    agent_name, conversation_id, speech[0].id, raw_response_hook=assert_live_status(404)
                )
            with pytest.raises(ResourceNotFoundError):
                await conversations.get_audio(agent_name, conversation_id, raw_response_hook=assert_live_status(404))
            with pytest.raises(ResourceNotFoundError):
                await conversations.get_audio_item(
                    agent_name, conversation_id, speech[0].id, raw_response_hook=assert_live_status(404)
                )
            with pytest.raises(ResourceNotFoundError):
                await conversations.download_audio(
                    agent_name, conversation_id, raw_response_hook=assert_live_status(404)
                )
            with pytest.raises(ResourceNotFoundError):
                await conversations.download_audio_item(
                    agent_name, conversation_id, speech[0].id, raw_response_hook=assert_live_status(404)
                )
            remaining = [
                value
                async for value in conversations.list(
                    agent_name, limit=1, order="asc", raw_response_hook=assert_live_status(200)
                )
            ]
            assert [value.id for value in remaining] == list(fixture.conversation_ids[1:])
