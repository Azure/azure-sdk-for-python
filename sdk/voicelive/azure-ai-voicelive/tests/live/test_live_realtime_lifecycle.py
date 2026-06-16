# pylint: disable=line-too-long,useless-suppression
# LIVE async tests using azure.ai.voicelive.aio (no mocks, no custom client)
# Conversation/response lifecycle operations: response cancel, item delete, input buffer clear.
from pathlib import Path

import pytest

pytest.importorskip(
    "aiohttp",
    reason="Skipping aio tests: aiohttp not installed (whl_no_aio).",
)

from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    InputTextContentPart,
    Modality,
    RequestSession,
    ResponseStatus,
    ServerEventConversationItemCreated,
    ServerEventConversationItemDeleted,
    ServerEventInputAudioBufferCleared,
    ServerEventResponseDone,
    ServerEventType,
    UserMessageItem,
)

from devtools_testutils import AzureRecordedTestCase
from .voicelive_preparer import VoiceLivePreparer
from ._live_helpers import (
    _get_trailing_silence_bytes,
    _load_audio_b64,
    _wait_for_event,
)


class TestRealtimeServiceLifecycle(AzureRecordedTestCase):

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_response_cancel(self, model: str, api_version: str, **kwargs):
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                modalities=[Modality.TEXT, Modality.AUDIO],
                instructions="You are a helpful assistant. Always answer with a long, detailed reply.",
            )
            await conn.session.update(session=session)
            await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 15)

            # Seed a user message so the model has something to respond to.
            await conn.conversation.item.create(
                item=UserMessageItem(
                    content=[InputTextContentPart(text="Tell me a very long story about the ocean.")]
                )
            )
            await conn.response.create()

            # Wait until the response is actually in progress, then cancel it.
            await _wait_for_event(conn, {ServerEventType.RESPONSE_CREATED}, 15)
            await conn.response.cancel()

            done = await _wait_for_event(conn, {ServerEventType.RESPONSE_DONE}, 20)
            assert isinstance(done, ServerEventResponseDone)
            assert done.response.status == ResponseStatus.CANCELLED

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_conversation_item_delete(self, model: str, api_version: str, **kwargs):
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(instructions="You are a helpful assistant.")
            await conn.session.update(session=session)
            await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 15)

            await conn.conversation.item.create(
                item=UserMessageItem(content=[InputTextContentPart(text="This item will be deleted.")])
            )
            created = await _wait_for_event(conn, {ServerEventType.CONVERSATION_ITEM_CREATED}, 15)
            assert isinstance(created, ServerEventConversationItemCreated)
            item_id = created.item.id

            await conn.conversation.item.delete(item_id=item_id)
            deleted = await _wait_for_event(conn, {ServerEventType.CONVERSATION_ITEM_DELETED}, 15)
            assert isinstance(deleted, ServerEventConversationItemDeleted)
            assert deleted.item_id == item_id

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_input_audio_buffer_clear(
        self, test_data_dir: Path, model: str, api_version: str, **kwargs
    ):
        file = test_data_dir / "largest_lake.wav"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            # Disable server VAD so the buffer is not auto-committed before we clear it.
            session = RequestSession(
                modalities=[Modality.TEXT, Modality.AUDIO],
                turn_detection=None,
            )
            await conn.session.update(session=session)
            await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 15)

            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes(duration_s=0.5))

            await conn.input_audio_buffer.clear()
            cleared = await _wait_for_event(conn, {ServerEventType.INPUT_AUDIO_BUFFER_CLEARED}, 15)
            assert isinstance(cleared, ServerEventInputAudioBufferCleared)
