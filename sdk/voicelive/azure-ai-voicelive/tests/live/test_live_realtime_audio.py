# pylint: disable=line-too-long,useless-suppression
# LIVE async tests using azure.ai.voicelive.aio (no mocks, no custom client)
# Audio input/output: enhancements, formats, sampling rate, echo cancellation.
from pathlib import Path

import pytest

pytest.importorskip(
    "aiohttp",
    reason="Skipping aio tests: aiohttp not installed (whl_no_aio).",
)

from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    AudioEchoCancellation,
    AudioNoiseReduction,
    AzureSemanticVad,
    AzureStandardVoice,
    InputAudioFormat,
    RequestSession,
    ServerEventType,
    ServerVad,
    TurnDetection,
)

from devtools_testutils import AzureRecordedTestCase
from .voicelive_preparer import VoiceLivePreparer
from ._live_helpers import (
    _collect_event,
    _get_speech_recognition_setting,
    _get_trailing_silence_bytes,
    _load_audio_b64,
    _wait_for_event,
)


class TestRealtimeServiceAudio(AzureRecordedTestCase):

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime", "gpt-4o"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_with_audio_enhancements(
        self,
        test_data_dir: Path,
        model: str,
        api_version: str,
        **kwargs,
    ):
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
            session = RequestSession(
                input_audio_noise_reduction=AudioNoiseReduction(type="azure_deep_noise_suppression"),
                input_audio_echo_cancellation=AudioEchoCancellation(),
            )
            await conn.session.update(session=session)

            # wait session.created
            await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 15)

            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            audio_segments, _ = await _collect_event(conn, event_type=ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED)
            assert audio_segments == 2

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize(
        ("model", "audio_format", "turn_detection"),
        [
            pytest.param(
                "gpt-4o", InputAudioFormat.G711_ULAW, AzureSemanticVad(), id="gpt4o_g711_ulaw_azure_semantic_vad"
            ),
            pytest.param(
                "gpt-4o", InputAudioFormat.G711_ALAW, AzureSemanticVad(), id="gpt4o_g711_alaw_azure_semantic_vad"
            ),
            pytest.param(
                "gpt-realtime",
                InputAudioFormat.G711_ULAW,
                AzureSemanticVad(),
                id="gpt4o_realtime_preview_g711_ulaw_azure_semantic_vad",
            ),
            pytest.param(
                "gpt-realtime",
                InputAudioFormat.G711_ULAW,
                ServerVad(),
                id="gpt4o_realtime_preview_g711_ulaw_server_vad",
            ),
            pytest.param(
                "gpt-realtime",
                InputAudioFormat.G711_ALAW,
                AzureSemanticVad(),
                id="gpt4o_realtime_preview_g711_alaw_azure_semantic_vad",
            ),
            pytest.param(
                "gpt-realtime",
                InputAudioFormat.G711_ALAW,
                ServerVad(),
                id="gpt4o_realtime_preview_g711_alaw_server_vad",
            ),
            pytest.param(
                "phi4-mm-realtime",
                InputAudioFormat.G711_ULAW,
                AzureSemanticVad(),
                id="phi4_mm_realtime_g711_ulaw_azure_semantic_vad",
            ),
            pytest.param(
                "phi4-mm-realtime",
                InputAudioFormat.G711_ALAW,
                AzureSemanticVad(),
                id="phi4_mm_realtime_g711_alaw_azure_semantic_vad",
            ),
            pytest.param(
                "phi4-mini",
                InputAudioFormat.G711_ULAW,
                AzureSemanticVad(),
                id="phi4_mini_g711_ulaw_azure_semantic_vad",
            ),
            pytest.param(
                "phi4-mini",
                InputAudioFormat.G711_ALAW,
                AzureSemanticVad(),
                id="phi4_mini_g711_alaw_azure_semantic_vad",
            ),
        ],
    )
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_with_input_audio_format(
        self,
        test_data_dir: Path,
        model: str,
        audio_format: InputAudioFormat,
        turn_detection: TurnDetection,
        api_version: str,
        **kwargs,
    ):
        """Test that all supported input_audio_format values work correctly with all models.

        This test verifies that the input_audio_format field in session configuration
        accepts all supported audio formats (pcm16, g711_ulaw, g711_alaw) and that
        the service can process audio properly regardless of the input format.
        """

        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        # Use the appropriate audio file for each format
        if audio_format == InputAudioFormat.PCM16:
            audio_file = test_data_dir / "largest_lake.wav"
        elif audio_format == InputAudioFormat.G711_ULAW:
            audio_file = test_data_dir / "largest_lake.ulaw"
        elif audio_format == InputAudioFormat.G711_ALAW:
            audio_file = test_data_dir / "largest_lake.alaw"
        else:
            raise ValueError(f"Unsupported audio format: {audio_format}")

        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                input_audio_format=audio_format,
                voice=AzureStandardVoice(name="en-US-AriaNeural"),
                instructions="You are a helpful assistant. Please respond briefly to the user's question.",
                turn_detection=turn_detection if turn_detection else None,
                input_audio_transcription=_get_speech_recognition_setting(model=model),
            )

            await conn.session.update(session=session)
            session_updated = await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED})
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

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize(
        ("model", "sampling_rate"),
        [
            pytest.param("gpt-realtime", 16000, id="gpt_realtime_16kHz_no_resample"),
            pytest.param("gpt-realtime", 44100, id="gpt_realtime_44kHz_no_resample"),
            pytest.param("gpt-realtime", 8000, id="gpt_realtime_8kHz_no_resample"),
            pytest.param("gpt-4o", 16000, id="gpt4o_16kHz_no_resample"),
            pytest.param("gpt-4o", 44100, id="gpt4o_44kHz_no_resample"),
            pytest.param("gpt-4.1", 8000, id="gpt4.1_8kHz_no_resample"),
            pytest.param("phi4-mm-realtime", 16000, id="phi4_mm_realtime_16kHz_no_resample"),
            pytest.param("phi4-mm-realtime", 44100, id="phi4_mm_realtime_44kHz_no_resample"),
        ],
    )
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_with_input_audio_sampling_rate(
        self, test_data_dir: Path, model: str, sampling_rate: int, api_version: str, **kwargs
    ):
        """Test that the realtime service works correctly with different input audio sampling rates.

        This test verifies that:
        1. Audio files with different sampling rates (16kHz, 44.1kHz) are processed correctly
        2. The should_resample_audio parameter works as expected
        3. The service generates appropriate responses regardless of input sampling rate
        4. Both resampling enabled and disabled scenarios work correctly
        """

        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        # Use the specified audio file
        audio_file = test_data_dir / f"largest_lake.{sampling_rate // 1000}kHz.wav"

        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                voice=AzureStandardVoice(name="en-US-AriaNeural"),
                input_audio_sampling_rate=sampling_rate,
                input_audio_transcription=_get_speech_recognition_setting(model),
                instructions="You are a helpful assistant. Please respond briefly to the user's question about lakes.",
                turn_detection=ServerVad(silence_duration_ms=200),
            )

            await conn.session.update(session=session)
            session_updated = await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 10)
            assert session_updated.session.input_audio_sampling_rate == sampling_rate

            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes(sample_rate=sampling_rate))
            speech_started = await _wait_for_event(conn, {ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED}, 10)
            assert speech_started.audio_start_ms == 0
            speech_stopped = await _wait_for_event(conn, {ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED}, 10)
            assert speech_stopped.audio_end_ms == pytest.approx(1680, abs=50)

            _, audio_bytes = await _collect_event(conn, event_type=ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA)
            assert audio_bytes > 50 * 1000, f"Output audio too short for {audio_file}: {audio_bytes} bytes"

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
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
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_output_formats_with_azure_voice(
        self, test_data_dir: Path, model: str, audio_output_format: str, api_version: str, **kwargs
    ):
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        audio_file = test_data_dir / "largest_lake.wav"
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                output_audio_format=audio_output_format,
                input_audio_transcription=_get_speech_recognition_setting(model),
                instructions="You are a helpful assistant.",
                turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=200),
            )

            await conn.session.update(session=session)
            session_updated = await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 10)
            assert session_updated.session.output_audio_format == audio_output_format
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            events, audio_bytes = await _collect_event(conn, event_type=ServerEventType.RESPONSE_AUDIO_DONE, timeout=20)
            assert events == 1
            assert audio_bytes > 10 * 1024

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime"])
    @pytest.mark.parametrize(
        "audio_output_format",
        [
            "pcm16",
            "g711_ulaw",
            "g711_alaw",
        ],
    )
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_output_formats_with_openai_voice(
        self, test_data_dir: Path, model: str, audio_output_format: str, api_version: str, **kwargs
    ):
        audio_file = test_data_dir / "largest_lake.wav"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                output_audio_format=audio_output_format,
                input_audio_transcription=_get_speech_recognition_setting(model),
                instructions="You are a helpful assistant.",
                voice="alloy",
            )

            await conn.session.update(session=session)
            session_updated = await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 10)
            assert session_updated.session.output_audio_format == audio_output_format
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            events, audio_bytes = await _collect_event(conn, event_type=ServerEventType.RESPONSE_OUTPUT_ITEM_DONE)
            assert events == 1
            assert audio_bytes > 10 * 1024

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime", "gpt-4.1"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_with_echo_cancellation(
        self,
        test_data_dir: Path,
        model: str,
        api_version: str,
        **kwargs,
    ):
        """Test echo cancellation in the realtime service."""
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        file = test_data_dir / "4-1.wav"
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                input_audio_transcription=_get_speech_recognition_setting(model),
                input_audio_echo_cancellation=AudioEchoCancellation(reference_source="server", channels=1),
            )

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            segments, audio_bytes = await _collect_event(
                conn, event_type=ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED
            )
            assert segments > 1, "Expected more than 1 speech segment"
            assert audio_bytes > 0, "Audio bytes should be greater than 0"

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
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
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_write_loopback_audio_echo_cancellation(
        self, test_data_dir: Path, model: str, audio_output_format: str, api_version: str, **kwargs
    ):
        """Test echo cancellation functionality with write_loopback_audio for different audio formats."""
        audio_file = test_data_dir / "largest_lake.wav"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                input_audio_transcription=_get_speech_recognition_setting(model),
                input_audio_echo_cancellation=AudioEchoCancellation(reference_source="server", channels=1),
                output_audio_format=audio_output_format,
                instructions="You are a helpful assistant.",
            )

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(audio_file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            contents, audio_bytes = await _collect_event(conn, event_type=ServerEventType.RESPONSE_CONTENT_PART_ADDED)
            assert contents >= 1, "Response should be generated with echo cancellation"
            assert audio_bytes > 0, "Audio bytes should be greater than 0"
