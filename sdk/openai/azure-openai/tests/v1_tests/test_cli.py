# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import subprocess
from conftest import (
    ENV_AZURE_OPENAI_ENDPOINT,
    ENV_AZURE_OPENAI_KEY,
    ENV_AZURE_OPENAI_API_VERSION,
    ENV_AZURE_OPENAI_COMPLETIONS_NAME,
    ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME,
    ENV_AZURE_OPENAI_AUDIO_NAME,
    ENV_AZURE_OPENAI_WHISPER_ENDPOINT,
    ENV_AZURE_OPENAI_WHISPER_KEY,
)

audio_test_file = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "./assets/hello.m4a"))


class TestCLI:
    """No support for embeddings CLI cmd"""

    def test_cli_completions(self):
        os.environ["AZURE_OPENAI_API_KEY"] = os.getenv(ENV_AZURE_OPENAI_KEY)
        try:
            result = subprocess.run(
                [
                    "openai",
                    "-a",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--azure-version={ENV_AZURE_OPENAI_API_VERSION}",
                    "api",
                    "completions.create",
                    "-m",
                    ENV_AZURE_OPENAI_COMPLETIONS_NAME,
                    "-p",
                    "hello world"
                ],
                check=True
            )
            assert result.returncode == 0
        finally:
            del os.environ['AZURE_OPENAI_API_KEY']

    def test_cli_chat_completions(self):
        os.environ["AZURE_OPENAI_API_KEY"] = os.getenv(ENV_AZURE_OPENAI_KEY)

        try:
            result = subprocess.run(
                [
                    "openai",
                    "-a",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--azure-version={ENV_AZURE_OPENAI_API_VERSION}",
                    "api",
                    "chat.completions.create",
                    "-m",
                    ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME,
                    "-g",
                    "user",
                    "how do I bake a chocolate cake?"
                ],
                check=True
            )
            assert result.returncode == 0
        finally:
            del os.environ['AZURE_OPENAI_API_KEY']

    @pytest.mark.skip("Unrecognized file format")
    def test_cli_audio_transcription(self):
        os.environ["AZURE_OPENAI_API_KEY"] = os.getenv(ENV_AZURE_OPENAI_WHISPER_KEY)

        try:
            result = subprocess.run(
                [
                    "openai",
                    "-a",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT)}",
                    f"--azure-version={ENV_AZURE_OPENAI_API_VERSION}",
                    "api",
                    "audio.transcriptions.create",
                    "-m",
                    ENV_AZURE_OPENAI_AUDIO_NAME,
                    "-f",
                    audio_test_file
                ],
                check=True
            )
            assert result.returncode == 0
        finally:
            del os.environ['AZURE_OPENAI_API_KEY']

    @pytest.mark.skip("Unrecognized file format")
    def test_cli_audio_translation(self):
        os.environ["AZURE_OPENAI_API_KEY"] = os.getenv(ENV_AZURE_OPENAI_WHISPER_KEY)

        try:
            result = subprocess.run(
                [
                    "openai",
                    "-a",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT)}",
                    f"--azure-version={ENV_AZURE_OPENAI_API_VERSION}",
                    "api",
                    "audio.translations.create",
                    "-m",
                    ENV_AZURE_OPENAI_AUDIO_NAME,
                    "-f",
                    audio_test_file
                ],
                check=True
            )
            assert result.returncode == 0
        finally:
            del os.environ['AZURE_OPENAI_API_KEY']

    def test_cli_models_list(self):
        os.environ["AZURE_OPENAI_API_KEY"] = os.getenv(ENV_AZURE_OPENAI_KEY)
        try:
            result = subprocess.run(
                [
                    "openai",
                    "-a",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--azure-version={ENV_AZURE_OPENAI_API_VERSION}",
                    "api",
                    "models.list",
                ],
                check=True
            )
            assert result.returncode == 0
        finally:
            del os.environ['AZURE_OPENAI_API_KEY']

    def test_cli_models_retrieve(self):
        os.environ["AZURE_OPENAI_API_KEY"] = os.getenv(ENV_AZURE_OPENAI_KEY)
        try:
            result = subprocess.run(
                [
                    "openai",
                    "-a",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--azure-version={ENV_AZURE_OPENAI_API_VERSION}",
                    "api",
                    "models.retrieve",
                    "-i",
                    ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME
                ],
                check=True
            )
            assert result.returncode == 0
        finally:
            del os.environ['AZURE_OPENAI_API_KEY']
