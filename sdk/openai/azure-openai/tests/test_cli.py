# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import sys
import pathlib
import subprocess
from devtools_testutils import AzureRecordedTestCase
from azure.identity import DefaultAzureCredential
from conftest import (
    ENV_AZURE_OPENAI_ENDPOINT,
    ENV_AZURE_OPENAI_KEY,
    LATEST,
    ENV_AZURE_OPENAI_COMPLETIONS_NAME,
    ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME,
    ENV_AZURE_OPENAI_AUDIO_NAME,
    ENV_AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT,
    ENV_AZURE_OPENAI_NORTHCENTRALUS_KEY,
    reload
)

audio_test_file = pathlib.Path(__file__).parent / "./assets/hello.m4a"


class TestCLI(AzureRecordedTestCase):
    """No support for embeddings CLI cmd"""

    def test_cli_env_vars_key(self):
        with reload():
            os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv(ENV_AZURE_OPENAI_ENDPOINT)
            os.environ["OPENAI_API_VERSION"] = LATEST
            os.environ["AZURE_OPENAI_API_KEY"] = os.getenv(ENV_AZURE_OPENAI_KEY)
            os.environ["OPENAI_API_TYPE"] = "azure"

            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
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

    def test_cli_env_vars_token(self):
        with reload():
            os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv(ENV_AZURE_OPENAI_ENDPOINT)
            os.environ["OPENAI_API_VERSION"] = LATEST
            os.environ["AZURE_OPENAI_AD_TOKEN"] = DefaultAzureCredential().get_token("https://cognitiveservices.azure.com/.default").token
            os.environ["OPENAI_API_TYPE"] = "azure"

            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
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

    def test_cli_ad_token(self):
        with reload():
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--api-version={LATEST}",
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

    def test_cli_completions(self):
        with reload():
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--api-version={LATEST}",
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

    def test_cli_chat_completions(self):
        with reload():
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--api-version={LATEST}",
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

    def test_cli_audio_transcription(self):
        with reload():
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT)}",
                    f"--api-version={LATEST}",
                    f"--api-key={os.getenv(ENV_AZURE_OPENAI_NORTHCENTRALUS_KEY)}",
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

    def test_cli_audio_translation(self):
        with reload():
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT)}",
                    f"--api-version={LATEST}",
                    f"--api-key={os.getenv(ENV_AZURE_OPENAI_NORTHCENTRALUS_KEY)}",
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

    def test_cli_models_list(self):
        with reload():
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--api-version={LATEST}",
                    f"--api-key={os.getenv(ENV_AZURE_OPENAI_KEY)}",
                    "api",
                    "models.list",
                ],
                check=True
            )
            assert result.returncode == 0

    def test_cli_models_retrieve(self):
        with reload():
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "openai",
                    "--api-type=azure",
                    f"--azure-endpoint={os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}",
                    f"--api-version={LATEST}",
                    f"--api-key={os.getenv(ENV_AZURE_OPENAI_KEY)}",
                    "api",
                    "models.retrieve",
                    "-i",
                    ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME
                ],
                check=True
            )
            assert result.returncode == 0
