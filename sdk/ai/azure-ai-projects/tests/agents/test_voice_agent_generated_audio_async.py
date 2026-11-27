# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async recorded success coverage for the Realtime generated-audio endpoints."""

from devtools_testutils import is_live
from devtools_testutils.aio import recorded_by_proxy_async
from test_base import TestBase
from realtime_interruption_test_base import (
    RealtimeInterruptionPreparer,
    add_interruption_sanitizers,
    assert_generated_status,
    assert_generated_wav,
    interruptionServicePreparer,
)


class TestVoiceAgentGeneratedAudioAsync(TestBase):
    @interruptionServicePreparer()
    @RealtimeInterruptionPreparer(require_generated_audio=True)
    @recorded_by_proxy_async()
    async def test_generated_audio_can_be_downloaded_async(self, interrupted_audio_fixture, **kwargs):
        fixture = interrupted_audio_fixture
        if is_live():
            add_interruption_sanitizers(fixture)
        async with self.create_async_client(**kwargs) as client:
            conversations = client.voice_agents.conversations
            item = (fixture.agent_name, fixture.conversation_id, fixture.item_id)
            metadata = await conversations.get_generated_audio_item(
                *item, raw_response_hook=assert_generated_status(200)
            )
            stream = await conversations.download_generated_audio_item(
                *item, raw_response_hook=assert_generated_status(200)
            )
            assert_generated_wav(b"".join([chunk async for chunk in stream]), metadata, fixture)
