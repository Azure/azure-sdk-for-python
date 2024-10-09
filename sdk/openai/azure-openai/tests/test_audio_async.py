# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import pathlib
import uuid
from devtools_testutils import AzureRecordedTestCase
from conftest import WHISPER_AZURE, OPENAI, PREVIEW, GA, configure_async, TTS_OPENAI, TTS_AZURE

audio_test_file = pathlib.Path(__file__).parent / "./assets/hello.m4a"
audio_long_test_file = pathlib.Path(__file__).parent / "./assets/wikipediaOcelot.wav"


@pytest.mark.live_test_only
class TestAudioAsync(AzureRecordedTestCase):

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")]
    )
    async def test_transcribe(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.transcriptions.create(
            file=open(audio_test_file, "rb"),
            **kwargs,
        )
        assert result.text == "Hello."

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_transcribe_raw(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.transcriptions.create(
            # file=open(audio_test_file, "rb").read(),
            # use file tuple for now
            file=("hello.m4a", open(audio_test_file, "rb").read(), "application/octet-stream"),
            **kwargs,
        )
        assert result.text == "Hello."

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")]
    )
    async def test_translate(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.translations.create(
            file=open(audio_test_file, "rb"),
            **kwargs,
        )
        assert result.text == "Hello."

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_translate_raw(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.translations.create(
            # file=open(audio_test_file, "rb").read(),
            # use file tuple for now
            file=("hello.m4a", open(audio_test_file, "rb").read(), "application/octet-stream"),
            **kwargs,
        )
        assert result.text == "Hello."

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_transcribe_verbose(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.transcriptions.create(
            file=open(audio_long_test_file, "rb"),
            response_format="verbose_json",
            **kwargs,
        )
        assert result.text == "The ocelot, Lepardus paradalis, is a small wild cat native to the southwestern " \
            "United States, Mexico, and Central and South America. This medium-sized cat is characterized by " \
            "solid black spots and streaks on its coat, round ears, and white neck and undersides. It weighs " \
            "between 8 and 15.5 kilograms, 18 and 34 pounds, and reaches 40 to 50 centimeters – 16 to 20 inches " \
            "– at the shoulders. It was first described by Carl Linnaeus in 1758. Two subspecies are recognized, " \
            "L. p. paradalis and L. p. mitis. Typically active during twilight and at night, the ocelot tends to " \
            "be solitary and territorial. It is efficient at climbing, leaping, and swimming. It preys on small " \
            "terrestrial mammals such as armadillo, opossum, and lagomorphs."
        assert result.task == "transcribe"
        assert result.language == "english"
        assert result.duration == 56.25
        for segment in result.segments:
            assert segment.id is not None
            assert segment.seek is not None
            assert segment.start is not None
            assert segment.end is not None
            assert segment.text is not None
            assert segment.tokens is not None
            assert segment.temperature is not None
            assert segment.avg_logprob is not None
            assert segment.compression_ratio is not None
            assert segment.no_speech_prob is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_transcribe_text(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.transcriptions.create(
            file=open(audio_test_file, "rb"),
            response_format="text",
            **kwargs,
        )
        assert result == "Hello.\n"

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_transcribe_srt(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.transcriptions.create(
            file=open(audio_test_file, "rb"),
            response_format="srt",
            **kwargs,
        )
        assert result == "1\n00:00:00,000 --> 00:00:02,000\nHello.\n\n\n"

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_transcribe_vtt(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.transcriptions.create(
            file=open(audio_test_file, "rb"),
            response_format="vtt",
            **kwargs,
        )
        assert result == "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nHello.\n\n"

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_translate_verbose(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.translations.create(
            file=open(audio_long_test_file, "rb"),
            response_format="verbose_json",
            **kwargs,
        )
        assert result.text == "The ocelot, Lepardus paradalis, is a small wild cat native to the southwestern " \
            "United States, Mexico, and Central and South America. This medium-sized cat is characterized by " \
            "solid black spots and streaks on its coat, round ears, and white neck and undersides. It weighs " \
            "between 8 and 15.5 kilograms, 18 and 34 pounds, and reaches 40 to 50 centimeters – 16 to 20 inches " \
            "– at the shoulders. It was first described by Carl Linnaeus in 1758. Two subspecies are recognized, " \
            "L. p. paradalis and L. p. mitis. Typically active during twilight and at night, the ocelot tends to " \
            "be solitary and territorial. It is efficient at climbing, leaping, and swimming. It preys on small " \
            "terrestrial mammals such as armadillo, opossum, and lagomorphs."
        assert result.task == "translate"
        assert result.language == "english"
        assert result.duration == 56.25
        for segment in result.segments:
            assert segment.id is not None
            assert segment.seek is not None
            assert segment.start is not None
            assert segment.end is not None
            assert segment.text is not None
            assert segment.tokens is not None
            assert segment.temperature is not None
            assert segment.avg_logprob is not None
            assert segment.compression_ratio is not None
            assert segment.no_speech_prob is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_translate_text(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.translations.create(
            file=open(audio_test_file, "rb"),
            response_format="text",
            **kwargs,
        )
        assert result == "Hello.\n"

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_translate_srt(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.translations.create(
            file=open(audio_test_file, "rb"),
            response_format="srt",
            **kwargs,
        )
        assert result == "1\n00:00:00,000 --> 00:00:02,000\nHello.\n\n\n"

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_translate_vtt(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.translations.create(
            file=open(audio_test_file, "rb"),
            response_format="vtt",
            **kwargs,
        )
        assert result == "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nHello.\n\n"

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_transcribe_options(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.transcriptions.create(
            file=open(audio_test_file, "rb"),
            temperature=0,
            language="en",
            prompt="Transcribe the text exactly as spoken.",
            **kwargs,
        )
        assert result.text == "Hello"

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(WHISPER_AZURE, GA), (WHISPER_AZURE, PREVIEW), (OPENAI, "v1")])
    async def test_translate_options(self, client_async, api_type, api_version, **kwargs):

        result = await client_async.audio.translations.create(
            file=open(audio_test_file, "rb"),
            temperature=0,
            prompt="Translate the text exactly as spoken.",
            **kwargs,
        )
        assert result.text == "Hello"

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(TTS_AZURE, PREVIEW), (TTS_OPENAI, "v1")]
    )
    async def test_tts(self, client_async, api_type, api_version, **kwargs):

        speech_file_path = pathlib.Path(__file__).parent / f"{uuid.uuid4()}.mp3"
        try:
            response = await client_async.audio.speech.create(
                voice="alloy",
                input="The quick brown fox jumped over the lazy dog.",
                **kwargs,
            )
            assert response.encoding
            assert response.content
            assert response.text
            response.write_to_file(speech_file_path)
        finally:
            os.remove(speech_file_path)

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(TTS_AZURE, PREVIEW), (TTS_OPENAI, "v1")])
    async def test_tts_hd(self, client_async, api_type, api_version, **kwargs):

        async with client_async.audio.speech.with_streaming_response.create(
            voice="echo",
            input="The quick brown fox jumped over the lazy dog.",
            model="tts-1-hd"
        ) as response:
            await response.read()

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(TTS_AZURE, PREVIEW), (TTS_OPENAI, "v1")])
    async def test_tts_response_format(self, client_async, api_type, api_version, **kwargs):

        speech_file_path = pathlib.Path(__file__).parent / f"{uuid.uuid4()}.flac"
        try:
            response = await client_async.audio.speech.create(
                voice="fable",
                input="The quick brown fox jumped over the lazy dog.",
                response_format="flac",
                **kwargs
            )
            assert response.encoding
            assert response.content
            assert response.text
            await response.astream_to_file(speech_file_path)  # deprecated
        finally:
            os.remove(speech_file_path)

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(TTS_AZURE, PREVIEW), (TTS_OPENAI, "v1")])
    async def test_tts_speed(self, client_async, api_type, api_version, **kwargs):

        speech_file_path = pathlib.Path(__file__).parent / f"{uuid.uuid4()}.mp3"
        try:
            response = await client_async.audio.speech.create(
                voice="onyx",
                input="The quick brown fox jumped over the lazy dog.",
                speed=3.0,
                **kwargs
            )
            assert response.encoding
            assert response.content
            assert response.text
            response.write_to_file(speech_file_path)
        finally:
            os.remove(speech_file_path)
