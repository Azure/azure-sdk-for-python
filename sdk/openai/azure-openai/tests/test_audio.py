# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import configure, AZURE, OPENAI, ALL

audio_test_file = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./assets/hello.m4a"))
audio_long_test_file = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./assets/wikipediaOcelot.wav"))

class TestAudio(AzureRecordedTestCase):

    @pytest.mark.parametrize("api_type", ALL)
    @configure
    def test_transcribe(self, azure_openai_creds, api_type):

        result = openai.Audio.transcribe(
            file=open(audio_test_file, "rb"),
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
        )
        assert result.text == "Hello."

    @pytest.mark.parametrize("api_type", ALL)
    @configure
    def test_transcribe_raw(self, azure_openai_creds, api_type):

        result = openai.Audio.transcribe_raw(
            file=open(audio_test_file, "rb").read(),
            filename="hello.m4a",
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
        )
        assert result.text == "Hello."

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_translate(self, azure_openai_creds, api_type):

        result = openai.Audio.translate(
            file=open(audio_test_file, "rb"),
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
        )
        assert result.text == "Hello."

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_translate_raw(self, azure_openai_creds, api_type):

        result = openai.Audio.translate_raw(
            file=open(audio_test_file, "rb").read(),
            filename="hello.m4a",
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
        )
        assert result.text == "Hello."

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_transcribe_verbose(self, azure_openai_creds, api_type):
        result = openai.Audio.transcribe(
            file=open(audio_long_test_file, "rb"),
            response_format="verbose_json",
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
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

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_transcribe_text(self, azure_openai_creds, api_type):
        result = openai.Audio.transcribe(
            file=open(audio_test_file, "rb"),
            response_format="text",
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
        )
        assert result == "Hello.\n"

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_transcribe_srt(self, azure_openai_creds, api_type):
        result = openai.Audio.transcribe(
            file=open(audio_test_file, "rb"),
            response_format="srt",
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
        )
        assert result == "1\n00:00:00,000 --> 00:00:02,000\nHello.\n\n\n"

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_transcribe_vtt(self, azure_openai_creds, api_type):
        result = openai.Audio.transcribe(
            file=open(audio_test_file, "rb"),
            response_format="vtt",
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
        )
        assert result == "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nHello.\n\n"

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_translate_verbose(self, azure_openai_creds, api_type):
        result = openai.Audio.translate(
            file=open(audio_long_test_file, "rb"),
            response_format="verbose_json",
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
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

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_translate_text(self, azure_openai_creds, api_type):
        result = openai.Audio.translate(
            file=open(audio_test_file, "rb"),
            response_format="text",
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
        )
        assert result == "Hello.\n"

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_translate_srt(self, azure_openai_creds, api_type):
        result = openai.Audio.translate(
            file=open(audio_test_file, "rb"),
            response_format="srt",
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
        )
        assert result == "1\n00:00:00,000 --> 00:00:02,000\nHello.\n\n\n"

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_translate_vtt(self, azure_openai_creds, api_type):
        result = openai.Audio.translate(
            file=open(audio_test_file, "rb"),
            response_format="vtt",
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
        )
        assert result == "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nHello.\n\n"

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_transcribe_options(self, azure_openai_creds, api_type):
        result = openai.Audio.transcribe(
            file=open(audio_test_file, "rb"),
            temperature=0,
            language="en",
            prompt="Transcribe the text exactly as spoken.",
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
        )
        assert result.text == "Hello"

    @pytest.mark.parametrize("api_type", [AZURE, OPENAI])
    @configure
    def test_translate_options(self, azure_openai_creds, api_type):
        result = openai.Audio.translate(
            file=open(audio_test_file, "rb"),
            temperature=0,
            prompt="Translate the text exactly as spoken.",
            model=azure_openai_creds["audio_model"],
            deployment_id=azure_openai_creds["audio_name"],
        )
        assert result.text == "Hello"
