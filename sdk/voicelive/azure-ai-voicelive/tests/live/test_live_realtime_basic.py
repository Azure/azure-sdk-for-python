# pylint: disable=line-too-long,useless-suppression
# LIVE async tests using azure.ai.voicelive.aio (no mocks, no custom client)
# Basic session lifecycle: connect, session update, retrieve, truncate.
from pathlib import Path

import pytest

pytest.importorskip(
    "aiohttp",
    reason="Skipping aio tests: aiohttp not installed (whl_no_aio).",
)

from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    AudioInputTranscriptionOptions,
    AzureStandardVoice,
    ContentPart,
    FunctionTool,
    Modality,
    RequestSession,
    ResponseMessageItem,
    ServerEventConversationItemRetrieved,
    ServerEventConversationItemTruncated,
    ServerEventResponseFunctionCallArgumentsDone,
    ServerEventResponseOutputItemDone,
    ServerEventType,
    ServerVad,
    ToolChoiceLiteral,
)

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from .voicelive_preparer import VoiceLivePreparer
from ._live_helpers import (
    _collect_event,
    _get_trailing_silence_bytes,
    _load_audio_b64,
    _wait_for_event,
)


class TestRealtimeServiceBasic(AzureRecordedTestCase):

    @VoiceLivePreparer()
    @recorded_by_proxy
    def smoke_test(self, **kwargs):
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        assert voicelive_openai_endpoint
        assert voicelive_openai_api_key

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime", "gpt-4.1", "phi4-mm-realtime", "phi4-mini"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service(self, test_data_dir: Path, model: str, api_version: str, **kwargs):
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        file = test_data_dir / "4-1.wav"
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            # text-only session
            session = RequestSession(modalities=[Modality.TEXT, Modality.AUDIO])
            await conn.session.update(session=session)

            # wait session.created
            await _wait_for_event(conn, {ServerEventType.SESSION_CREATED}, 15)
            await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 15)

            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))

            # Observe that we do NOT get a response.* automatically; we should at least see input_* events
            evt = await _wait_for_event(
                conn,
                {
                    ServerEventType.INPUT_AUDIO_BUFFER_COMMITTED,
                    ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED,
                    ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED,
                },
                20,
            )

            assert evt.type in {
                ServerEventType.INPUT_AUDIO_BUFFER_COMMITTED,
                ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED,
                ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED,
            }

            # We should see one of the audio response events eventually
            audio_delta_evt = await _wait_for_event(
                conn,
                {
                    ServerEventType.RESPONSE_AUDIO_DELTA,
                },
                30,
            )

            assert audio_delta_evt.type in {ServerEventType.RESPONSE_AUDIO_DELTA}
            assert audio_delta_evt.delta is not None and len(audio_delta_evt.delta) > 0

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime"])
    @pytest.mark.parametrize("api_version", ["2025-05-01-preview", "2026-04-10"])
    async def test_realtime_service_live_session_update(
        self,
        test_data_dir: Path,
        model: str,
        api_version: str,
        **kwargs,
    ):
        audio_file = test_data_dir / "ask_weather.wav"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                instructions="You are a helpful assistant that can answer questions.",
                voice=AzureStandardVoice(name="en-US-AvaMultilingualNeural"),
                input_audio_transcription=AudioInputTranscriptionOptions(model="azure-speech"),
                turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=200),
            )
            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            transcripts, audio_bytes = await _collect_event(
                conn, event_type=ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE, timeout=15
            )
            assert transcripts == 1
            assert audio_bytes > 50 * 1000

            tools = [
                FunctionTool(
                    name="get_weather",
                    description="Get the weather for a given location.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The location to get the weather for.",
                            },
                        },
                        "required": ["location"],
                    },
                )
            ]
            new_session = RequestSession(
                instructions="You are a helpful assistant with tools.",
                voice=AzureStandardVoice(name="en-US-AvaMultilingualNeural"),
                tools=tools,
                tool_choice=ToolChoiceLiteral.AUTO,
                turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=200),
            )
            await conn.session.update(session=new_session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())

            function_call_output = await _wait_for_event(conn, {ServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE})
            assert isinstance(function_call_output, ServerEventResponseFunctionCallArgumentsDone)
            assert function_call_output.name == "get_weather"
            assert function_call_output.arguments.replace(" ", "").replace("\n", "") in [
                '{"location":"北京"}',
                '{"location":"Beijing"}',
            ]

            await conn.response.create()
            transcripts, audio_bytes = await _collect_event(
                conn, event_type=ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE, timeout=15
            )
            assert audio_bytes > 50 * 1000
            assert transcripts == 1

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_retrieve_item(self, test_data_dir: Path, model: str, api_version: str, **kwargs):
        file = test_data_dir / "largest_lake.wav"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                instructions="You are a helpful assistant.",
                voice="alloy",
            )

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            output = await _wait_for_event(conn, [ServerEventType.RESPONSE_OUTPUT_ITEM_DONE])
            assert isinstance(output, ServerEventResponseOutputItemDone)
            await conn.conversation.item.retrieve(item_id=output.item.id)
            conversation_retrieved_event = await _wait_for_event(
                conn, [ServerEventType.CONVERSATION_ITEM_RETRIEVED], timeout_s=10
            )
            assert isinstance(
                conversation_retrieved_event, ServerEventConversationItemRetrieved
            ), f"Retrieved message should be an ServerEventConversationItemRetrieved: {conversation_retrieved_event}."
            assert isinstance(
                conversation_retrieved_event.item, ResponseMessageItem
            ), f"Retrieved item should be an ResponseMessageItem: {conversation_retrieved_event.item}."
            assert (
                conversation_retrieved_event.item.role == "assistant"
            ), "Retrieved item should be an assistant message."
            assert conversation_retrieved_event.item.content is not None, "Retrieved item should have content."
            assert isinstance(
                conversation_retrieved_event.item.content[0], ContentPart
            ), f"Retrieved item content should be audio: {conversation_retrieved_event.item.content[0]}."

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime"])
    @pytest.mark.parametrize("api_version", ["2025-05-01-preview", "2026-04-10"])
    async def test_realtime_service_truncate_item(self, test_data_dir: Path, model: str, api_version: str, **kwargs):
        file = test_data_dir / "largest_lake.wav"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                instructions="You are a helpful assistant.",
            )

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes(duration_s=0.5))

            output = await _wait_for_event(conn, [ServerEventType.RESPONSE_OUTPUT_ITEM_DONE])
            assert isinstance(output, ServerEventResponseOutputItemDone)

            await conn.conversation.item.truncate(item_id=output.item.id, content_index=0, audio_end_ms=1000)
            conversation_truncated_event = await _wait_for_event(
                conn, [ServerEventType.CONVERSATION_ITEM_TRUNCATED], timeout_s=10
            )
            assert isinstance(
                conversation_truncated_event, ServerEventConversationItemTruncated
            ), f"ItemTruncateMessage should be acknowledged: {conversation_truncated_event}."
            assert conversation_truncated_event.item_id == output.item.id
