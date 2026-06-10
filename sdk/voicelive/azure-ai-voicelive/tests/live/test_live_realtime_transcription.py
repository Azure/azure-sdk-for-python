# pylint: disable=line-too-long,useless-suppression
# LIVE async tests using azure.ai.voicelive.aio (no mocks, no custom client)
# Input audio transcription and filler-word removal scenarios.
from pathlib import Path
from typing import Literal

import pytest

pytest.importorskip(
    "aiohttp",
    reason="Skipping aio tests: aiohttp not installed (whl_no_aio).",
)

from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    AudioInputTranscriptionOptions,
    AzureSemanticVad,
    AzureSemanticVadMultilingual,
    Modality,
    RequestSession,
    ServerEventType,
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


class TestRealtimeServiceTranscription(AzureRecordedTestCase):

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime-mini"])
    @pytest.mark.parametrize(
        "transcription_model",
        [
            "whisper-1",
            "gpt-4o-transcribe",
            "gpt-4o-mini-transcribe",
            "gpt-4o-transcribe-diarize",
            "azure-speech",
            "mai-transcribe-1",
        ],
    )
    @pytest.mark.parametrize("api_version", ["2025-05-01-preview", "2026-01-01-preview"])
    async def test_realtime_service_input_audio_transcription(
        self,
        test_data_dir: Path,
        model: str,
        transcription_model: Literal[
            "whisper-1",
            "gpt-4o-transcribe",
            "gpt-4o-mini-transcribe",
            "gpt-4o-transcribe-diarize",
            "azure-speech",
            "mai-transcribe-1",
        ],
        api_version: str,
        **kwargs,
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
            input_audio_transcription = AudioInputTranscriptionOptions(
                model=transcription_model,
            )
            session = RequestSession(
                input_audio_transcription=input_audio_transcription,
                instructions="You are a helpful assistant.",
            )

            await conn.session.update(session=session)
            await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 10)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes(duration_s=0.5))
            input_audio_transcription_completed_evt = await _wait_for_event(
                conn,
                {
                    ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED,
                },
                30,
            )

            assert input_audio_transcription_completed_evt.transcript.strip() == "What's the largest lake in the world?"

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize(
        "test_audio_file",
        [
            "filler_word_24kHz.wav",
        ],
    )
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_with_filler_word_removal(
        self,
        test_data_dir: Path,
        test_audio_file: str,
        api_version: str,
        **kwargs,
    ):
        model = "gpt-realtime"
        file = test_data_dir / test_audio_file
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            turn_detection = AzureSemanticVad(remove_filler_words=True)
            session = RequestSession(modalities=[Modality.TEXT, Modality.AUDIO], turn_detection=turn_detection)

            await conn.session.update(session=session)
            evt = await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 10)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            audio_segments, _ = await _collect_event(conn, event_type=ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED)
            assert audio_segments == 0

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize(
        "test_audio_file",
        [
            "filler_word_24kHz.wav",
        ],
    )
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_with_filler_word_removal_multilingual(
        self, test_data_dir: Path, test_audio_file: str, api_version: str, **kwargs
    ):
        model = "gpt-realtime"
        file = test_data_dir / test_audio_file
        server_sd_conf = {
            "remove_filler_words": True,
        }

        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                turn_detection=AzureSemanticVadMultilingual(**server_sd_conf),
                input_audio_transcription=_get_speech_recognition_setting(model=model),
            )
            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            audio_segments, _ = await _collect_event(conn, event_type=ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED)
            assert audio_segments == 0
