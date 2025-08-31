# pylint: disable=line-too-long,useless-suppression
# tests/test_voicelive_realtime_async.py
# LIVE async tests using azure.ai.voicelive.aio (no mocks, no custom client)
import base64
import asyncio
from pathlib import Path
from typing import Iterator, Literal
import pytest
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    RequestSession,
    ServerVad,
    AzureStandardVoice,
    Modality,
    AudioFormat,
    ServerEventType,
    AudioEchoCancellation,
    AudioNoiseReduction,
    AzureSemanticVad,
    FunctionTool,
    ToolChoiceLiteral,
    AudioInputTranscriptionSettings,
    AudioTimestampType,
    Animation,
    AnimationOutputType,
    ServerEventConversationItemRetrieved,
    ServerEventConversationItemTruncated,
    AzureMultilingualSemanticVad,
    ResponseMessageItem,
    ContentPart,
    ItemType,
    TurnDetection,
    ToolChoiceFunctionObject,
    ToolChoiceFunctionObjectFunction,
    ResponseFunctionCallItem,
    ServerEventConversationItemCreated,
    EOUDetection,
)

def _b64_pcm_from_wav(path: Path) -> str:
    """Load 16-bit PCM WAV and return base64-encoded PCM16LE bytes (mono)."""
    import soundfile as sf  # local import; only needed for file-based tests

    audio, sr = sf.read(str(path), dtype="int16", always_2d=False)
    if audio.ndim > 1:
        audio = audio[:, 0]  # take first channel
    return base64.b64encode(audio.tobytes()).decode("utf-8")


def _load_audio_b64(path: Path, sample_rate=24000, trailing_silence: float = 2.0) -> str:
    with open(path, "rb") as f:
        audio_bytes = f.read()
    return base64.b64encode(audio_bytes).decode("utf-8")


def _get_trailing_silence_bytes(sample_rate: int = 24000, duration_s: float = 2.0) -> bytes:
    num_samples = int(sample_rate * duration_s)
    return b"\x00\x00" * num_samples  # 16-bit PCM silence


def _iter_audio_b64_chunks(path: Path, chunk_bytes: int = 10_240) -> Iterator[str]:
    """Yield base64-encoded chunks of the file, ~10 KB of raw bytes per chunk."""
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_bytes)
            if not chunk:
                break
            yield base64.b64encode(chunk).decode("utf-8")


def _get_speech_recognition_setting(model: str) -> AudioInputTranscriptionSettings:
    speech_recognition_model = (
        "whisper-1" if model.startswith(("gpt-4o-realtime", "gpt-4o-mini-realtime")) else "azure-speech"
    )
    return AudioInputTranscriptionSettings(model=speech_recognition_model, language="en-US")


async def _wait_for(conn, wanted_types: set, timeout_s: float = 10.0):
    """Wait until we receive any event whose type is in wanted_types."""

    async def _next():
        while True:
            evt = await conn.recv()
            print(f"Received event: {evt.type}")
            if evt.type in wanted_types:
                return evt

    return await asyncio.wait_for(_next(), timeout=timeout_s)


async def _collect_event(conn, *, event_type: ServerEventType, timeout: int = 10):
    evts = 0
    audio_bytes = 0
    loop = asyncio.get_event_loop()
    end = loop.time() + timeout

    while True:
        remaining = end - loop.time()
        if remaining <= 0:
            break

        try:
            evt = await asyncio.wait_for(conn.recv(), timeout=remaining)
            print(f"Received event: {evt.type}")
        except asyncio.TimeoutError:
            break  # no event arrived before the overall timeout

        if evt.type == event_type:
            evts += 1

        if evt.type == ServerEventType.RESPONSE_AUDIO_DELTA:
            audio_bytes += len(evt.delta)

    return evts, audio_bytes


async def _collect_audio_trans_outputs(conn, duration_s: float) -> int:
    trans_events = 0
    audio_events = 0
    try:
        async with asyncio.timeout(duration_s):
            while True:
                event = await conn.recv()  # no per-recv timeout needed
                if (
                    event.type == ServerEventType.RESPONSE_AUDIO_DELTA
                    or event.type == ServerEventType.RESPONSE_AUDIO_DONE
                ):
                    audio_events += 1

                if (
                    event.type == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA
                    or event.type == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE
                ):
                    trans_events += 1

    except TimeoutError:
        pass
    return audio_events, trans_events


class TestRealtimeService():
    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4o-realtime-preview", "gpt-4.1", "phi4-mm-realtime", "phi4-mini"])
    async def test_realtime_service(
        self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential
    ):
        file = test_data_dir / "4.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            # text-only session
            session = RequestSession(modalities=[Modality.TEXT, Modality.AUDIO])
            await conn.session.update(session=session)

            # wait session.created
            await _wait_for(conn, {ServerEventType.SESSION_CREATED}, 15)
            await _wait_for(conn, {ServerEventType.SESSION_UPDATED}, 15)

            await conn.input_audio_buffer.append(audio=_b64_pcm_from_wav(file))

            # Observe that we do NOT get a response.* automatically; we should at least see input_* events
            evt = await _wait_for(
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
            audio_delta_evt = await _wait_for(
                conn,
                {
                    ServerEventType.RESPONSE_AUDIO_DELTA,
                },
                30,
            )

            assert audio_delta_evt.type in {ServerEventType.RESPONSE_AUDIO_DELTA}
            assert audio_delta_evt.delta is not None and len(audio_delta_evt.delta) > 0

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4o-realtime-preview", "gpt-4.1"])
    async def test_realtime_service_with_audio_enhancements(
        self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential
    ):
        file = test_data_dir / "4.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            # text-only session
            session = RequestSession(
                input_audio_noise_reduction=AudioNoiseReduction(), input_audio_echo_cancellation=AudioEchoCancellation()
            )
            await conn.session.update(session=session)

            # wait session.created
            await _wait_for(conn, {ServerEventType.SESSION_CREATED}, 15)
            await _wait_for(conn, {ServerEventType.SESSION_UPDATED}, 15)

            await conn.input_audio_buffer.append(audio=_b64_pcm_from_wav(file))
            audio_segments, _ = await _collect_event(
                conn, event_type=ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED
            )
            assert audio_segments == 5

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize(
        ("model", "server_sd_conf"),
        [
            pytest.param("gpt-4o-realtime-preview", {}, id="gpt-4o-realtime-preview"),
            pytest.param(
                "gpt-4o-realtime-preview",
                {"window_size": 4, "distinct_ci_phones": 2, "require_vowel": True, "remove_filler_words": True},
                id="gpt-4o-realtime-preview-remove-filler-words",
            ),
            pytest.param("gpt-4.1", {}, id="cascaded-realtime"),
        ],
    )
    async def test_realtime_service_with_turn_detection(
        self,
        test_data_dir: Path,
        model: str,
        server_sd_conf: dict,
        endpoint: str,
        api_key_credential: AzureKeyCredential,
    ):
        file = test_data_dir / "4.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            turn_detection = None if not server_sd_conf else AzureSemanticVad(**server_sd_conf)
            session = RequestSession(modalities=[Modality.TEXT, Modality.AUDIO], turn_detection=turn_detection)

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_b64_pcm_from_wav(file))
            audio_delta_evt = await _wait_for(
                conn,
                {
                    ServerEventType.RESPONSE_AUDIO_DELTA,
                },
                30,
            )

            assert audio_delta_evt.type in {ServerEventType.RESPONSE_AUDIO_DELTA}
            assert audio_delta_evt.delta is not None and len(audio_delta_evt.delta) > 0

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize(
        ("model", "semantic_vad_params"),
        [
            pytest.param("gpt-4o-realtime-preview", {}, id="gpt-4o-realtime"),
            pytest.param(
                "gpt-4o-realtime-preview",
                {"window_size": 4, "distinct_ci_phones": 2, "require_vowel": True, "remove_filler_words": True},
                id="gpt-4o-realtime-remove-filler-words",
            ),
            pytest.param("gpt-4o", {}, id="cascaded-realtime"),
            pytest.param("gpt-4o", {"speech_duration_ms": 200}, id="cascaded-realtime"),
            pytest.param("gpt-4o", {"languages": ["en", "es"]}, id="cascaded-realtime"),
        ],
    )
    async def test_realtime_service_with_turn_detection_multilingual(
        self,
        test_data_dir: Path,
        model: str,
        semantic_vad_params: dict,
        endpoint: str,
        api_key_credential: AzureKeyCredential,
    ):
        file = test_data_dir / "4.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(turn_detection=AzureMultilingualSemanticVad(**semantic_vad_params))
            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_b64_pcm_from_wav(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())

            audio_segments, audio_bytes = await _collect_event(
                conn, event_type=ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED
            )
            assert audio_segments == 5
            assert audio_bytes > 0

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize(
        "test_audio_file",
        [
            "filler1_end_24kHz.wav",
            "filler2_end_24kHz.wav",
        ],
    )
    async def test_realtime_service_with_filler_word_removal(
        self, test_data_dir: Path, test_audio_file: str, endpoint: str, api_key_credential: AzureKeyCredential
    ):
        model = "gpt-4o-realtime-preview"
        file = test_data_dir / test_audio_file
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            turn_detection = AzureSemanticVad(
                window_size=2, distinct_ci_phones=2, require_vowel=True, remove_filler_words=True
            )
            session = RequestSession(modalities=[Modality.TEXT, Modality.AUDIO], turn_detection=turn_detection)

            await conn.session.update(session=session)
            await _wait_for(conn, {ServerEventType.SESSION_UPDATED}, 10)
            await conn.input_audio_buffer.append(audio=_b64_pcm_from_wav(file))
            audio_segments, _ = await _collect_event(
                conn, event_type=ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED
            )
            assert audio_segments == 1
    
    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize(
        "test_audio_file",
        [
            "filler1_end_24kHz.wav",
            # "filler2_end_24kHz.wav",
            # "filler3_end_24kHz.wav",
        ],
    )
    async def test_realtime_service_with_filler_word_removal_multilingual(
        self, test_data_dir: Path, test_audio_file: str, endpoint: str, api_key_credential: AzureKeyCredential
    ):
        model = "gpt-4o-realtime-preview"
        file = test_data_dir / test_audio_file
        server_sd_conf = {
            "window_size": 2,
            "distinct_ci_phones": 2,
            "require_vowel": False,
            "remove_filler_words": True,
        }
        
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                turn_detection=AzureMultilingualSemanticVad(**server_sd_conf),
                input_audio_transcription=_get_speech_recognition_setting(model=model))
            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_b64_pcm_from_wav(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            audio_segments, _ = await _collect_event(
                conn, event_type=ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED
            )
            assert audio_segments == 1

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4o-realtime", "gpt-4o"])
    async def test_realtime_service_tool_call(
        self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential
    ):
        audio_file = test_data_dir / "one-sentence.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
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
            await conn.input_audio_buffer.append(audio=_b64_pcm_from_wav(audio_file))
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
    
    @pytest.mark.asyncio
    @pytest.mark.skip
    @pytest.mark.parametrize("model", ["gpt-4o-realtime-preview-2025-06-03", "gpt-4o", "gpt-5-chat"])
    async def test_realtime_service_tool_choice(self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential):
        if "realtime" in model:
            pytest.skip("Tool choice is not supported in realtime models yet")
        audio_file = test_data_dir / "ask_weather.mp3"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
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
            tool_choice = ToolChoiceFunctionObject(function=ToolChoiceFunctionObjectFunction(name="get_time"))
            session = RequestSession(
                instructions="You are a helpful assistant with tools.",
                tools=tools,
                tool_choice=tool_choice,
                input_audio_transcription=_get_speech_recognition_setting(model=model),
            )
            await conn.session.update(session=session)
            
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await _wait_for(conn, {ServerEventType.SESSION_UPDATED}, 10)
            conversation_created_event = await _wait_for(conn, {ServerEventType.CONVERSATION_ITEM_CREATED})
            assert isinstance(conversation_created_event, ServerEventConversationItemCreated)
            assert isinstance(conversation_created_event.item, ResponseFunctionCallItem)
            assert conversation_created_event.item.type == ItemType.FUNCTION_CALL
            assert conversation_created_event.item.arguments in ['{"location":"北京"}', '{"location":"Beijing"}']
            assert conversation_created_event.item.function_name == "get_time"

    @pytest.mark.asyncio
    @pytest.mark.skip
    @pytest.mark.parametrize("model", ["gpt-4o-realtime", "gpt-4.1", "gpt-5"])
    async def test_realtime_service_tool_call_parameter(self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential):
        audio_file = test_data_dir / "ask_weather.mp3"
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
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                    instructions="You are a helpful assistant with tools. If you are asked about the weather, please respond with `I will get the weather for you. Please wait a moment.` and then call the get_weather function with the location parameter.",
                    tools=tools,
                    tool_choice=ToolChoiceLiteral.AUTO,
                    input_audio_transcription=_get_speech_recognition_setting(model=model),
                )
            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            conversation_created_event = await _wait_for(conn, {ServerEventType.CONVERSATION_ITEM_CREATED})
            print(conversation_created_event)
            assert isinstance(conversation_created_event, ServerEventConversationItemCreated)
            assert isinstance(conversation_created_event.item, ResponseFunctionCallItem)
            assert conversation_created_event.item.type == ItemType.FUNCTION_CALL
            assert conversation_created_event.item.arguments in ['{"location":"北京"}', '{"location":"Beijing"}']
            assert conversation_created_event.item.function_name == "get_weather"

    @pytest.mark.asyncio
    @pytest.mark.skip
    @pytest.mark.parametrize("model", ["gpt-4o", "gpt-4o-realtime"])
    async def test_realtime_service_live_session_update(self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential):
        audio_file = test_data_dir / "ask_weather.mp3"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                    instructions="You are a helpful assistant that can answer questions.",
                    voice=AzureStandardVoice(name="en-US-AvaMultilingualNeural"),
                    input_audio_transcription=_get_speech_recognition_setting(model=model),
                )
            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            content_part_added_events, audio_bytes = await _collect_event(conn, event_type=ServerEventType.RESPONSE_CONTENT_PART_ADDED)
            assert content_part_added_events == 1
            assert audio_bytes > 50 * 1000

            tools=[
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
                input_audio_transcription=_get_speech_recognition_setting(model=model),
                tools=tools,
                tool_choice=ToolChoiceLiteral.AUTO,
            )
            await conn.session.update(session=new_session)
            updated_session = await _wait_for(conn, {ServerEventType.SESSION_UPDATED})
            assert updated_session.tools == tools
            assert updated_session.tool_choice == ToolChoiceLiteral.AUTO

            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            conversation_created_event = await _wait_for(conn, {ServerEventType.CONVERSATION_ITEM_CREATED})
            print(conversation_created_event)
            assert isinstance(conversation_created_event, ServerEventConversationItemCreated)
            assert isinstance(conversation_created_event.item, ResponseFunctionCallItem)
            assert conversation_created_event.item.type == ItemType.FUNCTION_CALL
            assert conversation_created_event.item.arguments in ['{"location":"北京"}', '{"location":"Beijing"}']
            assert conversation_created_event.item.function_name == "get_weather"

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4o-realtime"])
    async def test_realtime_service_tool_call_no_audio_overlap(self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential):
        audio_file = test_data_dir / "audio_overlap.input_audio1.wav"
        tools=[
            FunctionTool(
                name="fetch_merchant_details",
                description="Get category name-Payments & Settlements':funds transferred to merchant’s bank post-deductions,issues collecting payments via QR/scanner,failed payments,MDR,payment mode activation/deactivation(wallet,credit card,postpaid,etc),customer details for payment,payment limits,payments not visible in app.'Lending':merchant loans via Paytm,loan applications,closure,offers,Easy Daily Instalments,loan settlement,payments towards EMI/EDI.'Profile':merchant account details,KYC,bank info,settlement timing/frequency requests,display name,address,shop details,account activation/deactivation,bank account update,settlement strategies (X times/day,next day).'Device':hardware issue with Soundbox/EDC,recurring rental charges,device return/deactivation,activation,accumulated dues,commission charges for payments,hardware malfunction for Soundbox/EDC.'Wealth':buying,storing,selling 24K digital gold via Gold Locker in P4B app,activating/canceling/restarting investment plans,viewing gold balance/investment history in Gold Locker.",
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
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                    instructions="You are a helpful assistant with tools. Please answer the question in detail before calling the function.",
                    input_audio_transcription=_get_speech_recognition_setting(model=model),
                    tools=tools,
                    tool_choice=ToolChoiceLiteral.AUTO,
                    voice=AzureStandardVoice(name="hi-IN-AartiNeural"),
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


    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4o-realtime"])
    @pytest.mark.parametrize("transcription_model", ["whisper-1", "gpt-4o-transcribe", "gpt-4o-mini-transcribe"])
    async def test_realtime_service_input_audio_transcription(
        self,
        test_data_dir: Path,
        model: str,
        transcription_model: Literal["whisper-1", "gpt-4o-transcribe", "gpt-4o-mini-transcribe"],
        endpoint: str,
        api_key_credential: AzureKeyCredential
    ):
        file = test_data_dir / "largest_lake.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            input_audio_transcription = AudioInputTranscriptionSettings(model=transcription_model)
            session = RequestSession(input_audio_transcription=input_audio_transcription)

            await conn.session.update(session=session)
            await _wait_for(conn, {ServerEventType.SESSION_UPDATED}, 10)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            input_audio_transcription_completed_evt = await _wait_for(
                conn,
                {
                    ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED,
                },
                30,
            )

            assert input_audio_transcription_completed_evt.transcript.strip() == "What's the largest lake in the world?"

    @pytest.mark.asyncio
    @pytest.mark.skip
    @pytest.mark.parametrize(
        ("model", "turn_detection_cls", "eou_model"),
        [
            pytest.param("gpt-4o", ServerVad, "semantic_detection_v1", id="server_vad_w_eou"),
            pytest.param("gpt-4o", AzureSemanticVad, "semantic_detection_v1", id="azure_semantic_vad_en_w_eou"),
            pytest.param(
                "gpt-4o",
                AzureMultilingualSemanticVad,
                "semantic_detection_v1",
                id="azure_semantic_vad_w_eou",
            ),
            pytest.param("gpt-4o", ServerVad, "semantic_detection_v1_en", id="server_vad_w_eou_en"),
            pytest.param("gpt-4o", AzureSemanticVad, "semantic_detection_v1_en", id="azure_semantic_vad_en_w_eou_en"),
            pytest.param(
                "gpt-4o",
                AzureMultilingualSemanticVad,
                "semantic_detection_v1_en",
                id="azure_semantic_vad_w_eou_en",
            ),
        ],
    )
    async def test_realtime_service_with_eou(
        self,
        test_data_dir: Path,
        model: str,
        turn_detection_cls: type[ServerVad | AzureSemanticVad | AzureMultilingualSemanticVad],
        eou_model: str,
        endpoint: str,
        api_key_credential: AzureKeyCredential,
    ):
        file = test_data_dir / "phone.wav"
        turn_detection = turn_detection_cls(end_of_utterance_detection=EOUDetection(model=eou_model))
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                turn_detection=turn_detection,
                input_audio_transcription=_get_speech_recognition_setting(model=model))

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            events, audio_bytes = await _collect_event(conn, event_type=ServerEventType.RESPONSE_DONE, timeout=30)
            assert events == 2
            assert audio_bytes > 0

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4o-realtime-preview", "gpt-4.1"])
    async def test_realtime_service_with_audio_timestamp_viseme(
        self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential
    ):
        file = test_data_dir / "4.wav"
        response_audio_word_timestamps = []
        response_blendshape_visemes = []
        audio_bytes = 0
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                voice=AzureStandardVoice(name="en-US-NancyNeural"),
                animation=Animation(outputs=[AnimationOutputType.VISEME_ID]),
                output_audio_timestamp_types=[AudioTimestampType.WORD],
            )

            await conn.session.update(session=session)
            await _wait_for(conn, {ServerEventType.SESSION_UPDATED}, 10)
            await conn.input_audio_buffer.append(audio=_b64_pcm_from_wav(file))

            timeout_s = 10
            start = asyncio.get_event_loop().time()
            while True:
                if asyncio.get_event_loop().time() - start > timeout_s:
                    break

                try:
                    event = await asyncio.wait_for(conn.recv(), timeout=2)  # short per-recv timeout
                except asyncio.TimeoutError:
                    continue

                if event.type == ServerEventType.RESPONSE_ANIMATION_VISEME_DELTA:
                    response_blendshape_visemes.append(event)

                if event.type == ServerEventType.RESPONSE_AUDIO_TIMESTAMP_DELTA:
                    response_audio_word_timestamps.append(event)

                if event.type == ServerEventType.RESPONSE_AUDIO_DELTA:
                    audio_bytes += len(event.delta)

            assert audio_bytes > 0
            assert len(response_audio_word_timestamps) > 0
            assert len(response_blendshape_visemes) > 0

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4o-realtime", "gpt-4o", "phi4-mm-realtime", "phi4-mini"])
    async def test_realtime_service_wo_turn_detection(
        self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential
    ):
        file = test_data_dir / "ask_weather.mp3"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(turn_detection={"type": "none"})

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            audio_events, trans_events = await _collect_audio_trans_outputs(conn, 5)
            assert audio_events == 0
            assert trans_events == 0
            await conn.input_audio_buffer.commit()
            audio_events, trans_events = await _collect_audio_trans_outputs(conn, 5)
            assert audio_events == 0
            assert trans_events == 0
            await conn.response.create()
            audio_events, trans_events = await _collect_audio_trans_outputs(conn, 10)
            assert audio_events > 0
            assert trans_events > 0

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4o-realtime", "gpt-4.1", "phi4-mm-realtime"])
    async def test_realtime_service_with_voice_properties(
        self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential
    ):
        file = test_data_dir / "largest_lake.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                voice=AzureStandardVoice(
                    name="en-us-emma:DragonHDLatestNeural", temperature=0.7, rate="1.2", prefer_locales=["en-IN"]
                ),
                input_audio_transcription=_get_speech_recognition_setting(model=model), 
            )

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            content_part_added_events, _ = await _collect_event(conn, event_type=ServerEventType.RESPONSE_CONTENT_PART_ADDED)
            assert content_part_added_events == 1

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4o-realtime"])
    async def test_realtime_service_retrieve_item(
        self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential
    ):
        file = test_data_dir / "largest_lake.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                instructions="You are a helpful assistant.",
                voice="alloy",
            )

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            conversation_item_created = await _wait_for(conn, [ServerEventType.CONVERSATION_ITEM_CREATED])
            content_part_added = await _wait_for(conn, [ServerEventType.RESPONSE_CONTENT_PART_ADDED])
            assert conversation_item_created.item.id == content_part_added.item_id

            await conn.conversation.item.retrieve(item_id=content_part_added.item_id)
            conversation_retrieved_event = await _wait_for(
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

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4o-realtime"])
    async def test_realtime_service_truncate_item(
        self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential
    ):
        file = test_data_dir / "largest_lake.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                instructions="You are a helpful assistant.",
            )

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))

            conversation_item_created = await _wait_for(conn, [ServerEventType.CONVERSATION_ITEM_CREATED], timeout_s=10)
            content_part_added = await _wait_for(conn, [ServerEventType.RESPONSE_CONTENT_PART_ADDED], timeout_s=10)
            assert content_part_added.part.type == "audio"
            assert conversation_item_created.item.id == content_part_added.item_id

            await conn.conversation.item.truncate(item_id=content_part_added.item_id, content_index=0, audio_end_ms=200)
            conversation_retrieved_event = await _wait_for(
                conn, [ServerEventType.CONVERSATION_ITEM_TRUNCATED], timeout_s=10
            )
            assert isinstance(
                conversation_retrieved_event, ServerEventConversationItemTruncated
            ), f"Retrieved item should be an ServerEventConversationItemTruncated: {conversation_retrieved_event}."

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize(
        ("model", "audio_format", "turn_detection"),
        [
            pytest.param("gpt-4o", AudioFormat.G711_ULAW, AzureSemanticVad(), id="gpt4o_g711_ulaw_azure_semantic_vad"),
            pytest.param("gpt-4o", AudioFormat.G711_ALAW, AzureSemanticVad(), id="gpt4o_g711_alaw_azure_semantic_vad"),
            pytest.param(
                "gpt-4o-realtime-preview",
                AudioFormat.G711_ULAW,
                AzureSemanticVad(),
                id="gpt4o_realtime_preview_g711_ulaw_azure_semantic_vad",
            ),
            pytest.param(
                "gpt-4o-realtime-preview",
                AudioFormat.G711_ULAW,
                ServerVad(),
                id="gpt4o_realtime_preview_g711_ulaw_server_vad",
            ),
            pytest.param(
                "gpt-4o-realtime-preview",
                AudioFormat.G711_ALAW,
                AzureSemanticVad(),
                id="gpt4o_realtime_preview_g711_alaw_azure_semantic_vad",
            ),
            pytest.param(
                "gpt-4o-realtime-preview",
                AudioFormat.G711_ALAW,
                ServerVad(),
                id="gpt4o_realtime_preview_g711_alaw_server_vad",
            ),
            pytest.param(
                "phi4-mm-realtime",
                AudioFormat.G711_ULAW,
                AzureSemanticVad(),
                id="phi4_mm_realtime_g711_ulaw_azure_semantic_vad",
            ),
            pytest.param(
                "phi4-mm-realtime",
                AudioFormat.G711_ALAW,
                AzureSemanticVad(),
                id="phi4_mm_realtime_g711_alaw_azure_semantic_vad",
            ),
            pytest.param(
                "phi4-mini",
                AudioFormat.G711_ULAW,
                AzureSemanticVad(),
                id="phi4_mini_g711_ulaw_azure_semantic_vad",
            ),
            pytest.param(
                "phi4-mini",
                AudioFormat.G711_ALAW,
                AzureSemanticVad(),
                id="phi4_mini_g711_alaw_azure_semantic_vad",
            ),
        ],
    )
    async def test_realtime_service_with_input_audio_format(
        self,
        test_data_dir: Path,
        model: str,
        audio_format: AudioFormat,
        turn_detection: TurnDetection,
        endpoint: str,
        api_key_credential: AzureKeyCredential,
    ):
        """Test that all supported input_audio_format values work correctly with all models.

        This test verifies that the input_audio_format field in session configuration
        accepts all supported audio formats (pcm16, g711_ulaw, g711_alaw) and that
        the service can process audio properly regardless of the input format.
        """

        # Use the appropriate audio file for each format
        if audio_format == AudioFormat.PCM16:
            audio_file = test_data_dir / "largest_lake.wav"
        elif audio_format == AudioFormat.G711_ULAW:
            audio_file = test_data_dir / "largest_lake.ulaw"
        elif audio_format == AudioFormat.G711_ALAW:
            audio_file = test_data_dir / "largest_lake.alaw"
        else:
            raise ValueError(f"Unsupported audio format: {audio_format}")

        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                input_audio_format=audio_format,
                voice=AzureStandardVoice(name="en-US-AriaNeural"),
                instructions="You are a helpful assistant. Please respond briefly to the user's question.",
                turn_detection=turn_detection if turn_detection else None,
                input_audio_transcription=_get_speech_recognition_setting(model=model)
            )

            await conn.session.update(session=session)
            session_updated = await _wait_for(conn, {ServerEventType.SESSION_UPDATED})
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            assert (
                session_updated.session.input_audio_format == audio_format
            ), f"Expected audio format {audio_format}, got {session_updated.session.input_audio_format}"
            assert session_updated.session.input_audio_sampling_rate == 24000 if audio_format == "pcm16" else 8000, (
                f"Expected sampling rate 24000 for pcm16, got {session_updated.session.input_audio_sampling_rate}"
                if audio_format == "pcm16"
                else f"Expected sampling rate 8000 for g711 formats, got {session_updated.session.input_audio_sampling_rate}"
            )

            _, audio_bytes = await _collect_event(conn, event_type=None)
            assert audio_bytes > 50 * 1000, f"Output audio too short for {audio_format} format: {audio_bytes} bytes"

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize(
        ("model", "sampling_rate"),
        [
            pytest.param("gpt-4o-realtime-preview", 16000, id="gpt4o_realtime_16kHz_no_resample"),
            pytest.param("gpt-4o-realtime", 44100, id="gpt4o_realtime_44kHz_no_resample"),
            pytest.param("gpt-4o-realtime", 8000, id="gpt4o_realtime_8kHz_no_resample"),
            pytest.param("gpt-4o", 16000, id="gpt4o_16kHz_no_resample"),
            pytest.param("gpt-4o", 44100, id="gpt4o_44kHz_no_resample"),
            pytest.param("gpt-4.1", 8000, id="gpt4.1_8kHz_no_resample"),
            pytest.param("phi4-mm-realtime", 16000, id="phi4_mm_realtime_16kHz_no_resample"),
            pytest.param("phi4-mm-realtime", 44100, id="phi4_mm_realtime_44kHz_no_resample"),
        ],
    )
    async def test_realtime_service_with_input_audio_sampling_rate(
        self, test_data_dir: Path, model: str, sampling_rate: int, endpoint: str, api_key_credential: AzureKeyCredential
    ):
        """Test that the realtime service works correctly with different input audio sampling rates.

        This test verifies that:
        1. Audio files with different sampling rates (16kHz, 44.1kHz) are processed correctly
        2. The should_resample_audio parameter works as expected
        3. The service generates appropriate responses regardless of input sampling rate
        4. Both resampling enabled and disabled scenarios work correctly
        """

        # Use the specified audio file
        audio_file = test_data_dir / f"largest_lake.{sampling_rate // 1000}kHz.wav"

        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                voice=AzureStandardVoice(name="en-US-AriaNeural"),
                input_audio_sampling_rate=sampling_rate,
                input_audio_transcription=_get_speech_recognition_setting(model),
                instructions="You are a helpful assistant. Please respond briefly to the user's question about lakes.",
                turn_detection=ServerVad(),
            )

            await conn.session.update(session=session)
            session_updated = await _wait_for(conn, {ServerEventType.SESSION_UPDATED}, 10)
            assert session_updated.session.input_audio_sampling_rate == sampling_rate

            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes(sample_rate=sampling_rate))
            speech_started = await _wait_for(conn, {ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED}, 10)
            assert speech_started.audio_start_ms == 0
            speech_stopped = await _wait_for(conn, {ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED}, 10)
            assert speech_stopped.audio_end_ms == pytest.approx(1664, rel=2e-2)

            _, audio_bytes = await _collect_event(
                conn, event_type=ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA
            )
            assert audio_bytes > 50 * 1000, f"Output audio too short for {audio_file}: {audio_bytes} bytes"

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4.1", "phi4-mini"])
    @pytest.mark.parametrize(
        "audio_output_format",
        [
            "pcm16",
            "pcm16_8000hz",
            "pcm16_16000hz",
            "pcm16_22050hz",
            "pcm16_24000hz",
            "pcm16_44100hz",
            "pcm16_48000hz",
            "g711_ulaw",
            "g711_alaw",
        ],
    )
    async def test_output_formats_with_azure_voice(
        self,
        test_data_dir: Path,
        model: str,
        audio_output_format: str,
        endpoint: str,
        api_key_credential: AzureKeyCredential,
    ):
        audio_file = test_data_dir / "largest_lake.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                output_audio_format=audio_output_format,
                input_audio_transcription=_get_speech_recognition_setting(model),
                instructions="You are a helpful assistant.",
                turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=200),
            )

            await conn.session.update(session=session)
            session_updated = await _wait_for(conn, {ServerEventType.SESSION_UPDATED}, 10)
            assert session_updated.session.output_audio_format == audio_output_format
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            events, audio_bytes = await _collect_event(
                conn, event_type=ServerEventType.RESPONSE_AUDIO_DONE, timeout=20
            )
            assert events == 1
            assert audio_bytes > 10 * 1024

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4o-realtime"])
    @pytest.mark.parametrize(
        "audio_output_format",
        [
            "pcm16",
            "g711_ulaw",
            "g711_alaw",
        ],
    )
    async def test_output_formats_with_openai_voice(
        self,
        test_data_dir: Path,
        model: str,
        audio_output_format: str,
        endpoint: str,
        api_key_credential: AzureKeyCredential,
    ):
        audio_file = test_data_dir / "largest_lake.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                output_audio_format=audio_output_format,
                input_audio_transcription=_get_speech_recognition_setting(model),
                instructions="You are a helpful assistant.",
                voice="alloy",
            )

            await conn.session.update(session=session)
            session_updated = await _wait_for(conn, {ServerEventType.SESSION_UPDATED}, 10)
            assert session_updated.session.output_audio_format == audio_output_format
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            events, audio_bytes = await _collect_event(
                conn, event_type=ServerEventType.RESPONSE_OUTPUT_ITEM_DONE
            )
            assert events == 1
            assert audio_bytes > 10 * 1024

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4o-realtime-preview", "gpt-4.1"])
    async def test_realtime_service_with_echo_cancellation(
        self, test_data_dir: Path, model: str, endpoint: str, api_key_credential: AzureKeyCredential
    ):
        """Test echo cancellation in the realtime service."""
        file = test_data_dir / "4.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                input_audio_transcription=_get_speech_recognition_setting(model),
                input_audio_echo_cancellation=AudioEchoCancellation(),
            )

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            segments, audio_bytes = await _collect_event(
                conn, event_type=ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED
            )
            assert segments > 1, "Expected more than 1 speech segment"
            assert audio_bytes > 0, "Audio bytes should be greater than 0"

    @pytest.mark.asyncio
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-4.1", "phi4-mm-realtime", "phi4-mini"])
    @pytest.mark.parametrize(
        "audio_output_format",
        [
            "pcm16",
            "pcm16_8000hz",
            "pcm16_16000hz",
            "pcm16_22050hz",
            "pcm16_24000hz",
            "pcm16_44100hz",
            "pcm16_48000hz",
            "g711_ulaw",
            "g711_alaw",
        ],
    )
    async def test_write_loopback_audio_echo_cancellation(
        self,
        test_data_dir: Path,
        model: str,
        audio_output_format: str,
        endpoint: str,
        api_key_credential: AzureKeyCredential,
    ):
        """Test echo cancellation functionality with write_loopback_audio for different audio formats."""
        audio_file = test_data_dir / "largest_lake.wav"
        async with connect(endpoint=endpoint, credential=api_key_credential, model=model) as conn:
            session = RequestSession(
                input_audio_transcription=_get_speech_recognition_setting(model),
                input_audio_echo_cancellation=AudioEchoCancellation(),
                output_audio_format=audio_output_format,
                instructions="You are a helpful assistant.",
            )

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            contents, audio_bytes = await _collect_event(
                conn, event_type=ServerEventType.RESPONSE_CONTENT_PART_ADDED
            )
            assert contents >= 1, "Response should be generated with echo cancellation"
            assert audio_bytes > 0, "Audio bytes should be greater than 0"
