# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Test Proxy recorded coverage of all nine dedicated GPT Live REST operations.

Recording needs FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_VOICE_LIVE_MODEL_NAME.
The latter is the existing GPT Live deployment name, not a model catalog ID.
The outer fixture preparer creates owned stored sessions outside HTTP recording;
playback performs REST calls only. These cases remain enabled without recordings
so missing Test Proxy assets are visible rather than hidden by a skip marker.
"""

import pytest

from azure.ai.projects import models
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import is_live, recorded_by_proxy
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


class TestVoiceAgentLiveConversations(TestBase):
    @liveConversationServicePreparer()
    @LiveConversationPreparer()
    @recorded_by_proxy()
    def test_live_conversation_rest_lifecycle(self, live_conversation_fixture, **kwargs):
        self._test_live_conversation_rest_lifecycle(live_conversation_fixture, **kwargs)

    def _test_live_conversation_rest_lifecycle(self, live_conversation_fixture, **kwargs):
        fixture = live_conversation_fixture
        if is_live():
            add_live_conversation_sanitizers(fixture)
        with self.create_client(allow_preview=True, **kwargs) as client:
            conversations = client.beta.voice_agents.live_conversations
            agent_name, conversation_id = fixture.agent_name, fixture.conversation_ids[0]
            listed = list(
                conversations.list(agent_name, limit=1, order="asc", raw_response_hook=assert_live_status(200))
            )
            assert [value.id for value in listed] == list(fixture.conversation_ids)
            for value in listed:
                assert_completed_conversation(value, value.id)
            detail = conversations.get(agent_name, conversation_id, raw_response_hook=assert_live_status(200))
            assert_completed_conversation(detail, conversation_id)

            items = list(
                conversations.list_items(
                    agent_name, conversation_id, limit=1, order="asc", raw_response_hook=assert_live_status(200)
                )
            )
            assert items and len({item.id for item in items}) == len(items)
            assert all(isinstance(item, models.VoiceAgentLiveConversationItem) for item in items)
            speech = [item for item in items if isinstance(item, models.VoiceAgentLiveOutputConversationItem)]
            assert speech, "Stored greeting speech must exercise item audio, not just metadata/list routes"
            for item in speech:
                assert_speech_item(item)
                fetched = conversations.get_item(
                    agent_name, conversation_id, item.id, raw_response_hook=assert_live_status(200)
                )
                fetched = assert_speech_item(fetched, item.id)
                assert fetched.transcription == item.transcription
                audio = conversations.get_audio_item(
                    agent_name, conversation_id, item.id, raw_response_hook=assert_live_status(200)
                )
                assert_audio_metadata(audio, conversation_id, item_id=item.id)
                assert_wav(
                    b"".join(
                        conversations.download_audio_item(
                            agent_name, conversation_id, item.id, raw_response_hook=assert_live_status(200)
                        )
                    ),
                    audio,
                )
            recording = conversations.get_audio(agent_name, conversation_id, raw_response_hook=assert_live_status(200))
            assert_audio_metadata(recording, conversation_id)
            assert_wav(
                b"".join(
                    conversations.download_audio(agent_name, conversation_id, raw_response_hook=assert_live_status(200))
                ),
                recording,
            )

            conversations.delete(agent_name, conversation_id, raw_response_hook=assert_live_status(204))
            with pytest.raises(ResourceNotFoundError):
                conversations.get(agent_name, conversation_id, raw_response_hook=assert_live_status(404))
            with pytest.raises(ResourceNotFoundError):
                conversations.get_item(
                    agent_name, conversation_id, speech[0].id, raw_response_hook=assert_live_status(404)
                )
            with pytest.raises(ResourceNotFoundError):
                conversations.get_audio(agent_name, conversation_id, raw_response_hook=assert_live_status(404))
            with pytest.raises(ResourceNotFoundError):
                conversations.get_audio_item(
                    agent_name, conversation_id, speech[0].id, raw_response_hook=assert_live_status(404)
                )
            with pytest.raises(ResourceNotFoundError):
                list(
                    conversations.download_audio(agent_name, conversation_id, raw_response_hook=assert_live_status(404))
                )
            with pytest.raises(ResourceNotFoundError):
                list(
                    conversations.download_audio_item(
                        agent_name, conversation_id, speech[0].id, raw_response_hook=assert_live_status(404)
                    )
                )
            remaining = list(
                conversations.list(agent_name, limit=1, order="asc", raw_response_hook=assert_live_status(200))
            )
            assert [value.id for value in remaining] == list(fixture.conversation_ids[1:])
