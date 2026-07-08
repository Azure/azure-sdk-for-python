# pylint: disable=line-too-long,useless-suppression
# LIVE async tests using azure.ai.voicelive.aio (no mocks, no custom client)
# Avatar / viseme / voice property scenarios.
import asyncio

from pathlib import Path

import pytest

pytest.importorskip(
    "aiohttp",
    reason="Skipping aio tests: aiohttp not installed (whl_no_aio).",
)

from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    Animation,
    AnimationOutputType,
    AudioTimestampType,
    AzureStandardVoice,
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


class TestRealtimeServiceAvatar(AzureRecordedTestCase):

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime", "gpt-4.1"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_with_audio_timestamp_viseme(
        self,
        test_data_dir: Path,
        model: str,
        api_version: str,
        **kwargs,
    ):
        file = test_data_dir / "4-1.wav"
        response_audio_word_timestamps = []
        response_blendshape_visemes = []
        audio_bytes = 0
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                voice=AzureStandardVoice(name="en-US-NancyNeural"),
                animation=Animation(outputs=[AnimationOutputType.VISEME_ID]),
                output_audio_timestamp_types=[AudioTimestampType.WORD],
            )

            await conn.session.update(session=session)
            await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 10)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))

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

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime", "gpt-4.1", "phi4-mm-realtime"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_with_voice_properties(
        self,
        test_data_dir: Path,
        model: str,
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
            session = RequestSession(
                voice=AzureStandardVoice(
                    name="en-us-emma:DragonHDLatestNeural", temperature=0.7, rate="1.2", prefer_locales=["en-IN"]
                ),
                input_audio_transcription=_get_speech_recognition_setting(model=model),
            )

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
            content_part_added_events, _ = await _collect_event(
                conn, event_type=ServerEventType.RESPONSE_CONTENT_PART_ADDED
            )
            assert content_part_added_events == 1
