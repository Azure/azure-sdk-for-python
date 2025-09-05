"""
Pytest configuration for Azure AI Voice Live SDK tests.
"""

import pytest
import os
import base64
from devtools_testutils import (
    test_proxy,
)
from unittest.mock import MagicMock
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from pathlib import Path

ENV_API_KEY = "AZURE_OPENAI_KEY"
ENV_OPENAI_ENDPOINT = "AZURE_OPENAI_ENDPOINT"

TEST_ENDPOINT = os.getenv(ENV_OPENAI_ENDPOINT)
TEST_API_KEY = os.getenv(ENV_API_KEY)

@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return

@pytest.fixture
def endpoint() -> str:
    return TEST_ENDPOINT


@pytest.fixture
def credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()


@pytest.fixture
def api_key_credential() -> AzureKeyCredential:
    """Create an AzureKeyCredential fixture."""
    return AzureKeyCredential(TEST_API_KEY)


@pytest.fixture
def test_audio_data():
    """Create a sample audio data fixture."""
    # 1 second of silence (PCM16, 24kHz, mono)
    dummy_audio = b"\x00\x00" * 24000
    return dummy_audio


@pytest.fixture
def test_audio_base64(test_audio_data):
    """Create a base64-encoded sample audio data fixture."""
    return base64.b64encode(test_audio_data).decode("utf-8")


@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parent / "data"
