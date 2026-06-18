# pylint: disable=line-too-long,useless-suppression
# LIVE async tests using azure.ai.voicelive.aio (no mocks, no custom client)
# Function/tool calling scenarios.
import asyncio
import json

from pathlib import Path
from typing import Any, Mapping, Union

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
    FunctionCallOutputItem,
    FunctionTool,
    ItemType,
    RequestSession,
    ResponseFunctionCallItem,
    ServerEventConversationItemCreated,
    ServerEventResponseCreated,
    ServerEventResponseFunctionCallArgumentsDelta,
    ServerEventResponseFunctionCallArgumentsDone,
    ServerEventType,
    ServerVad,
    ToolChoiceFunctionSelection,
    ToolChoiceLiteral,
)

from devtools_testutils import AzureRecordedTestCase
from .voicelive_preparer import VoiceLivePreparer
from ._live_helpers import (
    _get_speech_recognition_setting,
    _get_trailing_silence_bytes,
    _load_audio_b64,
    _wait_for_event,
    _wait_for_match,
)


class TestRealtimeServiceTools(AzureRecordedTestCase):

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime", "gpt-4o"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_tool_call(self, test_data_dir: Path, model: str, api_version: str, **kwargs):
        audio_file = test_data_dir / "4-1.wav"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            tools = [
                FunctionTool(
                    name="assess_pronunciation", description="Assess pronunciation of the last user input speech"
                )
            ]
            session = RequestSession(
                instructions="You are a teacher to a student who is learning English. You are talking with student with speech. For each user input speech, you need to call the assess_pronunciation function to assess the pronunciation of the last user input speech, and then give feedback to the student.",
                tools=tools,
                tool_choice=ToolChoiceLiteral.AUTO,
                input_audio_transcription=_get_speech_recognition_setting(model=model),
                voice=AzureStandardVoice(name="en-US-AriaNeural"),
            )

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.response.create()
            timeout_s = 10
            conversation_created_events = []
            function_call_results = []
            start = asyncio.get_event_loop().time()
            while True:
                if asyncio.get_event_loop().time() - start > timeout_s:
                    break

                try:
                    event = await asyncio.wait_for(conn.recv(), timeout=2)  # short per-recv timeout
                except asyncio.TimeoutError:
                    continue

                if (
                    event.type == ServerEventType.CONVERSATION_ITEM_CREATED
                    and event.item.type == ItemType.FUNCTION_CALL
                ):
                    conversation_created_events.append(event)

                if event.type == ServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA:
                    function_call_results.append(event)

            assert len(function_call_results) > 0

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime", "gpt-4o", "gpt-5-chat"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_tool_choice(self, test_data_dir: Path, model: str, api_version: str, **kwargs):
        if "realtime" in model:
            pytest.skip("Tool choice is not supported in realtime models yet")
        audio_file = test_data_dir / "ask_weather.wav"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
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
                ),
                FunctionTool(
                    name="get_time",
                    description="Get the current time in a given location.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The location to get the current time for.",
                            },
                        },
                        "required": ["location"],
                    },
                ),
            ]
            tool_choice = ToolChoiceFunctionSelection(name="get_time")
            session = RequestSession(
                instructions="You are a helpful assistant with tools.",
                tools=tools,
                tool_choice=tool_choice,
                input_audio_transcription=AudioInputTranscriptionOptions(model="azure-speech"),
                turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=200),
            )
            await conn.session.update(session=session)
            await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED})
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())

            timeout_s = 10
            start = asyncio.get_event_loop().time()
            conversation_created = None
            while True:
                if asyncio.get_event_loop().time() - start > timeout_s:
                    break

                try:
                    event = await asyncio.wait_for(conn.recv(), timeout=2)  # short per-recv timeout
                except asyncio.TimeoutError:
                    continue

                if (
                    event.type == ServerEventType.CONVERSATION_ITEM_CREATED
                    and event.item.type == ItemType.FUNCTION_CALL
                ):
                    conversation_created = event
                    break

            assert isinstance(conversation_created, ServerEventConversationItemCreated)
            assert isinstance(conversation_created.item, ResponseFunctionCallItem)
            assert conversation_created.item.type == ItemType.FUNCTION_CALL
            assert conversation_created.item.name == "get_time"

            function_delta = await _wait_for_event(conn, {ServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA})
            assert isinstance(function_delta, ServerEventResponseFunctionCallArgumentsDelta)

            function_done = await _wait_for_event(conn, {ServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE})
            assert isinstance(function_done, ServerEventResponseFunctionCallArgumentsDone)
            assert function_done.arguments.replace(" ", "").replace("\n", "") in [
                '{"location":"北京"}',
                '{"location":"Beijing"}',
            ]
            assert function_done.name == "get_time"

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime", "gpt-4.1", "gpt-5", "gpt-5.1", "gpt-5.2", "phi4-mm-realtime"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_tool_call_parameter(
        self,
        test_data_dir: Path,
        model: str,
        api_version: str,
        **kwargs,
    ):
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")

        def get_weather(arguments: Union[str, Mapping[str, Any]]) -> str:
            return json.dumps({"location": "Beijing", "weather": "sunny", "temp_c": 25})

        if "realtime" in model:
            pytest.skip("Tool choice is not supported in realtime models yet")
        audio_file = test_data_dir / "ask_weather.wav"
        tools = [
            FunctionTool(
                name="get_weather",
                description="Retrieve the weather of given location.",
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
        instructions = "You are a helpful assistant with tools."
        if model != "phi4-mm-realtime":
            instructions += " If you are asked about the weather, please respond with `I will get the weather for you. Please wait a moment.` and then call the get_weather function with the location parameter."
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                instructions=instructions,
                tools=tools,
                tool_choice=ToolChoiceLiteral.AUTO,
                input_audio_transcription=AudioInputTranscriptionOptions(model="azure-speech"),
                turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=200),
            )
            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())

            response_created = await _wait_for_event(conn, {ServerEventType.RESPONSE_CREATED})
            isinstance(response_created, ServerEventResponseCreated)

            conversation_created = await _wait_for_match(
                conn,
                lambda e: e.type == ServerEventType.CONVERSATION_ITEM_CREATED and e.item.type == ItemType.FUNCTION_CALL,
            )
            assert isinstance(conversation_created, ServerEventConversationItemCreated)
            assert isinstance(conversation_created.item, ResponseFunctionCallItem)
            assert conversation_created.item.type == ItemType.FUNCTION_CALL
            assert conversation_created.item.name == "get_weather"
            call_id = conversation_created.item.call_id
            previous_item_id = conversation_created.item.id

            function_done = await _wait_for_event(conn, {ServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE})
            assert isinstance(function_done, ServerEventResponseFunctionCallArgumentsDone)
            assert function_done.call_id == call_id
            assert function_done.arguments in ['{"location":"北京"}', '{"location":"Beijing"}']
            await _wait_for_event(conn, {ServerEventType.RESPONSE_DONE})

            tool_output = get_weather(function_done.arguments)
            await conn.conversation.item.create(
                previous_item_id=previous_item_id, item=FunctionCallOutputItem(call_id=call_id, output=tool_output)
            )
            await conn.response.create()

            response = await _wait_for_match(
                conn, lambda e: e.type == ServerEventType.RESPONSE_OUTPUT_ITEM_DONE and e.item.id != previous_item_id
            )
            transcript = response.item.content[0].transcript
            assert "晴" in transcript or "sunny" in transcript
            assert "25" in transcript

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.skip()
    @pytest.mark.parametrize("model", ["gpt-4o", "gpt-realtime"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_tool_call_no_audio_overlap(
        self,
        test_data_dir: Path,
        model: str,
        api_version: str,
        **kwargs,
    ):
        audio_file = test_data_dir / "audio_overlap.wav"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        tools = [
            FunctionTool(
                name="fetch_merchant_details",
                description="Get category name-Payments & Settlements':funds transferred to merchant’s bank post-deductions,issues collecting payments via QR/scanner,failed payments,MDR,payment mode activation/deactivation(wallet,credit card,postpaid,etc),customer details for payment,payment limits,payments not visible in app.'Lending':merchant loans via Pay,loan applications,closure,offers,Easy Daily Instalments,loan settlement,payments towards EMI/EDI.'Profile':merchant account details,KYC,bank info,settlement timing/frequency requests,display name,address,shop details,account activation/deactivation,bank account update,settlement strategies (X times/day,next day).'Device':hardware issue with Soundbox/EDC,recurring rental charges,device return/deactivation,activation,accumulated dues,commission charges for payments,hardware malfunction for Soundbox/EDC.'Wealth':buying,storing,selling 24K digital gold via Gold Locker in P4B app,activating/canceling/restarting investment plans,viewing gold balance/investment history in Gold Locker.",
                parameters={
                    "type": "object",
                    "properties": {
                        "intent_name": {
                            "type": "string",
                            "description": "The intent category that best matches the merchant's query (Payments and Settlements, Profile, Device, Lending, Wealth).",
                        },
                    },
                    "required": ["intent_name"],
                },
            )
        ]
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                instructions="You are a helpful assistant with tools. Please answer the question in detail before calling the function.",
                input_audio_transcription=_get_speech_recognition_setting(model=model),
                tools=tools,
                tool_choice=ToolChoiceLiteral.AUTO,
            )
            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            timeout_s = 10
            start = asyncio.get_event_loop().time()
            message_types = set()
            while True:
                if asyncio.get_event_loop().time() - start > timeout_s:
                    break

                try:
                    event = await asyncio.wait_for(conn.recv(), timeout=2)  # short per-recv timeout
                except asyncio.TimeoutError:
                    continue

                if event.type == ServerEventType.CONVERSATION_ITEM_CREATED:
                    message_types.add(event.item.type)

            assert len(message_types) == 2
