# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Recorded generated-audio behavior after cancelling a real response."""

import pytest

from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import is_live, recorded_by_proxy
from test_base import TestBase
from realtime_interruption_test_base import (
    RealtimeInterruptionPreparer,
    add_interruption_sanitizers,
    assert_conversation_deleted,
    assert_generated_metadata,
    assert_generated_status,
    assert_generated_wav,
    interruptionServicePreparer,
)


class TestVoiceAgentGeneratedAudio(TestBase):
    @interruptionServicePreparer()
    @RealtimeInterruptionPreparer()
    @recorded_by_proxy()
    def test_interrupted_generated_audio(self, interrupted_audio_fixture, **kwargs):
        fixture = interrupted_audio_fixture
        if is_live():
            add_interruption_sanitizers(fixture)
        with self.create_client(**kwargs) as client:
            conversations = client.voice_agents.conversations
            try:
                metadata = conversations.get_generated_audio_item(
                    fixture.agent_name,
                    fixture.conversation_id,
                    fixture.item_id,
                    raw_response_hook=assert_generated_status((200, 404)),
                )
            except ResourceNotFoundError as error:
                # Cancellation may stop rendering before a complete generated artifact exists.
                assert error.status_code == 404
                assert error.error and error.error.code == "not_found"
                assert error.message and "generated audio" in error.message.casefold()
                assert fixture.item_id in error.message
                with pytest.raises(ResourceNotFoundError) as download_error:
                    b"".join(
                        conversations.download_generated_audio_item(
                            fixture.agent_name,
                            fixture.conversation_id,
                            fixture.item_id,
                            raw_response_hook=assert_generated_status(404),
                        )
                    )
                assert download_error.value.status_code == 404
            else:
                assert_generated_metadata(metadata, fixture)
                content = b"".join(
                    conversations.download_generated_audio_item(
                        fixture.agent_name,
                        fixture.conversation_id,
                        fixture.item_id,
                        raw_response_hook=assert_generated_status(200),
                    )
                )
                assert_generated_wav(content, metadata, fixture)
            conversations.delete(
                fixture.agent_name,
                fixture.conversation_id,
                raw_response_hook=assert_conversation_deleted,
            )
            for operation, streamed in (
                (conversations.get_generated_audio_item, False),
                (conversations.download_generated_audio_item, True),
            ):
                with pytest.raises(ResourceNotFoundError):
                    result = operation(
                        fixture.agent_name,
                        fixture.conversation_id,
                        fixture.item_id,
                        raw_response_hook=assert_generated_status(404),
                    )
                    if streamed:
                        list(result)
