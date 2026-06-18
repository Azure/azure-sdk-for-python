# pylint: disable=line-too-long,useless-suppression
# LIVE async tests using azure.ai.voicelive.aio (no mocks, no custom client)
# Turn detection / VAD / end-of-utterance scenarios.
from pathlib import Path
from typing import Type, Union

import pytest

pytest.importorskip(
    "aiohttp",
    reason="Skipping aio tests: aiohttp not installed (whl_no_aio).",
)

from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    AzureSemanticDetection,
    AzureSemanticDetectionEn,
    AzureSemanticVad,
    AzureSemanticVadMultilingual,
    RequestSession,
    ServerEventType,
    ServerVad,
)

from devtools_testutils import AzureRecordedTestCase
from .voicelive_preparer import VoiceLivePreparer
from ._live_helpers import (
    _collect_audio_trans_outputs,
    _collect_event,
    _get_speech_recognition_setting,
    _get_trailing_silence_bytes,
    _load_audio_b64,
    _wait_for_event,
)


class TestRealtimeServiceTurnDetection(AzureRecordedTestCase):

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize(
        ("model", "server_sd_conf"),
        [
            pytest.param(
                "gpt-realtime",
                {"type": "azure_semantic_vad", "speech_duration_assistant_speaking_ms": 800},
                id="gpt-realtime",
            ),
            pytest.param(
                "gpt-4o",
                {"type": "azure_semantic_vad", "speech_duration_assistant_speaking_ms": 800},
                id="cascaded-realtime",
            ),
        ],
    )
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_with_turn_detection_long_tts_vad_duration(
        self, test_data_dir: Path, model: str, server_sd_conf: dict, api_version: str, **kwargs
    ):
        file = test_data_dir / "4-1.wav"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            turn_detection = None if not server_sd_conf else server_sd_conf
            session = RequestSession(turn_detection=turn_detection)

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
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
    @pytest.mark.parametrize(
        ("model", "semantic_vad_params"),
        [
            pytest.param("gpt-realtime", {}, id="gpt-realtime"),
            # pytest.param(
            #     "gpt-realtime",
            #     {"window_size": 4, "distinct_ci_phones": 2, "require_vowel": True, "remove_filler_words": True},
            #     id="gpt-realtime-remove-filler-words",
            # ),
            pytest.param("gpt-4o", {}, id="cascaded-realtime"),
            pytest.param("gpt-4o", {"speech_duration_ms": 200}, id="cascaded-realtime"),
            pytest.param("gpt-4o", {"languages": ["en", "es"]}, id="cascaded-realtime"),
        ],
    )
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_with_turn_detection_multilingual(
        self, test_data_dir: Path, model: str, semantic_vad_params: dict, api_version: str, **kwargs
    ):
        file = test_data_dir / "4-1.wav"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(turn_detection=AzureSemanticVadMultilingual(**semantic_vad_params))
            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())

            audio_segments, audio_bytes = await _collect_event(
                conn, event_type=ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED
            )
            assert audio_segments == 2
            assert audio_bytes > 0

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize(
        ("model", "turn_detection_cls", "end_of_detection"),
        [
            pytest.param("gpt-4o", ServerVad, AzureSemanticDetection, id="server_vad_w_eou"),
            pytest.param("gpt-4o", AzureSemanticVad, AzureSemanticDetection, id="azure_semantic_vad_en_w_eou"),
            pytest.param(
                "gpt-4o",
                AzureSemanticVadMultilingual,
                AzureSemanticDetection,
                id="azure_semantic_vad_w_eou",
            ),
            pytest.param("gpt-4o", ServerVad, AzureSemanticDetectionEn, id="server_vad_w_eou_en"),
            pytest.param("gpt-4o", AzureSemanticVad, AzureSemanticDetectionEn, id="azure_semantic_vad_en_w_eou_en"),
            pytest.param(
                "gpt-4o",
                AzureSemanticVadMultilingual,
                AzureSemanticDetectionEn,
                id="azure_semantic_vad_w_eou_en",
            ),
        ],
    )
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_with_eou(
        self,
        test_data_dir: Path,
        model: str,
        turn_detection_cls: Type[Union["ServerVad", "AzureSemanticVad", "AzureSemanticVadMultilingual"]],
        end_of_detection: Type[Union["AzureSemanticDetection", "AzureSemanticDetectionEn"]],
        api_version: str,
        **kwargs,
    ):
        file = test_data_dir / "4-1.wav"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        turn_detection = turn_detection_cls(end_of_utterance_detection=end_of_detection(timeout_ms=2000))
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(
                turn_detection=turn_detection,
                input_audio_transcription=_get_speech_recognition_setting(model=model),
            )

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes(duration_s=0.5))
            events, audio_bytes = await _collect_event(conn, event_type=ServerEventType.RESPONSE_DONE)
            assert events > 0
            assert audio_bytes > 0

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime", "gpt-4o", "phi4-mm-realtime", "phi4-mini"])
    @pytest.mark.parametrize("api_version", ["2025-10-01", "2026-04-10"])
    async def test_realtime_service_wo_turn_detection(
        self,
        test_data_dir: Path,
        model: str,
        api_version: str,
        **kwargs,
    ):
        file = test_data_dir / "ask_weather.mp3"
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")
        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
            api_version=api_version,
        ) as conn:
            session = RequestSession(turn_detection=None)

            await conn.session.update(session=session)
            await conn.input_audio_buffer.append(audio=_load_audio_b64(file))
            await conn.input_audio_buffer.append(audio=_get_trailing_silence_bytes())
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
