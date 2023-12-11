# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import subprocess
from devtools_testutils import AzureRecordedTestCase
from azure.identity import DefaultAzureCredential
from conftest import (
    ENV_AZURE_OPENAI_ENDPOINT,
    ENV_AZURE_OPENAI_KEY,
    ENV_AZURE_OPENAI_API_VERSION,
    ENV_AZURE_OPENAI_COMPLETIONS_NAME,
    ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME,
    ENV_AZURE_OPENAI_AUDIO_NAME,
    ENV_AZURE_OPENAI_WHISPER_ENDPOINT,
    ENV_AZURE_OPENAI_WHISPER_KEY,
    configure,
    AZURE,
    reload
)

audio_test_file = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "./assets/hello.m4a"))


class TestCLI(AzureRecordedTestCase):
    """No support for embeddings CLI cmd"""

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_cli_env_vars_key(self, client, azure_openai_creds, api_type, **kwargs):
        with reload():
            os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv(ENV_AZURE_OPENAI_ENDPOINT)
            os.environ["OPENAI_API_VERSION"] = ENV_AZURE_OPENAI_API_VERSION
            os.environ["AZURE_OPENAI_API_KEY"] = os.getenv(ENV_AZURE_OPENAI_KEY)
            os.environ["OPENAI_API_TYPE"] = "azure"

            try:
                result = subprocess.run(
                    [
                        "openai",
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
                del os.environ['AZURE_OPENAI_ENDPOINT']
                del os.environ['AZURE_OPENAI_API_KEY']
                del os.environ['OPENAI_API_VERSION']
                del os.environ["OPENAI_API_TYPE"]

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_cli_env_vars_token(self, client, azure_openai_creds, api_type, **kwargs):
        with reload():
            os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv(ENV_AZURE_OPENAI_ENDPOINT)
            os.environ["OPENAI_API_VERSION"] = ENV_AZURE_OPENAI_API_VERSION
            os.environ["AZURE_OPENAI_AD_TOKEN"] = DefaultAzureCredential().get_token("https://cognitiveservices.azure.com/.default").token
            os.environ["OPENAI_API_TYPE"] = "azure"

            try:
                result = subprocess.run(
                    [
                        "openai",
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
                del os.environ['AZURE_OPENAI_ENDPOINT']
                del os.environ['AZURE_OPENAI_AD_TOKEN']
                del os.environ['OPENAI_API_VERSION']
                del os.environ["OPENAI_API_TYPE"]

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_cli_ad_token(self, client, azure_openai_creds, api_type, **kwargs):
        with reload():
            result = subprocess.run(
                [
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--api-version={ENV_AZURE_OPENAI_API_VERSION}",
                    f"--azure-ad-token={DefaultAzureCredential().get_token('https://cognitiveservices.azure.com/.default').token}",
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

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_cli_completions(self, client, azure_openai_creds, api_type, **kwargs):
        with reload():
            result = subprocess.run(
                [
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--api-version={ENV_AZURE_OPENAI_API_VERSION}",
                    f"--api-key={os.getenv(ENV_AZURE_OPENAI_KEY)}",
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

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_cli_chat_completions(self, client, azure_openai_creds, api_type, **kwargs):
        with reload():
            result = subprocess.run(
                [
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--api-version={ENV_AZURE_OPENAI_API_VERSION}",
                    f"--api-key={os.getenv(ENV_AZURE_OPENAI_KEY)}",
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

    @pytest.mark.skip("Unrecognized file format")
    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_cli_audio_transcription(self, client, azure_openai_creds, api_type, **kwargs):
        with reload():
            result = subprocess.run(
                [
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT)}",
                    f"--api-version={ENV_AZURE_OPENAI_API_VERSION}",
                    f"--api-key={os.getenv(ENV_AZURE_OPENAI_WHISPER_KEY)}",
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

    @pytest.mark.skip("Unrecognized file format")
    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_cli_audio_translation(self, client, azure_openai_creds, api_type, **kwargs):
        with reload():
            result = subprocess.run(
                [
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT)}",
                    f"--api-version={ENV_AZURE_OPENAI_API_VERSION}",
                    f"--api-key={os.getenv(ENV_AZURE_OPENAI_WHISPER_KEY)}",
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

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_cli_models_list(self, client, azure_openai_creds, api_type, **kwargs):
        with reload():
            result = subprocess.run(
                [
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--api-version={ENV_AZURE_OPENAI_API_VERSION}",
                    f"--api-key={os.getenv(ENV_AZURE_OPENAI_KEY)}",
                    "api",
                    "models.list",
                ],
                check=True
            )
            assert result.returncode == 0


    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_cli_models_retrieve(self, client, azure_openai_creds, api_type, **kwargs):
        with reload():
            result = subprocess.run(
                [
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--api-version={ENV_AZURE_OPENAI_API_VERSION}",
                    f"--api-key={os.getenv(ENV_AZURE_OPENAI_KEY)}",
                    "api",
                    "models.retrieve",
                    "-i",
                    ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME
                ],
                check=True
            )
            assert result.returncode == 0
