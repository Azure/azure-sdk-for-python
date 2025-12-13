# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
import pytest
from dotenv import load_dotenv
from devtools_testutils import (
    test_proxy,
    add_general_regex_sanitizer,
    add_general_string_sanitizer,
    add_body_key_sanitizer,
    add_header_regex_sanitizer,
    add_uri_regex_sanitizer,
    set_custom_default_matcher,
)

load_dotenv()


# Define fixtures for test parameters
@pytest.fixture(scope="session")
def transcription_endpoint():
    """Fixture providing the transcription endpoint."""
    return os.environ.get(
        "TRANSCRIPTION_ENDPOINT", 
        "https://fakeendpoint.cognitiveservices.azure.com"
    )


@pytest.fixture(scope="session")
def transcription_api_key():
    """Fixture providing the transcription API key."""
    return os.environ.get("TRANSCRIPTION_API_KEY", "fake-api-key")


@pytest.fixture(scope="session")
def transcription_test_audio_url():
    """Fixture providing a test audio URL."""
    return os.environ.get(
        "TRANSCRIPTION_TEST_AUDIO_URL",
        "https://example.com/test-audio.wav"
    )


# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    """Start test proxy server for recording and playback."""
    return


# For security, please avoid recording sensitive identity information in recordings
@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # Configure matcher to ignore authentication header differences
    # This allows recordings made with API key auth to work with AAD auth in CI
    set_custom_default_matcher(
        excluded_headers="Authorization,Ocp-Apim-Subscription-Key",
        ignored_headers="Authorization,Ocp-Apim-Subscription-Key"
    )
    
    # Sanitize subscription and tenant IDs if they exist
    # Only sanitize if the values are actually set (not default fake values)
    transcription_subscription_id = os.environ.get("TRANSCRIPTION_SUBSCRIPTION_ID", "")
    if transcription_subscription_id and transcription_subscription_id != "00000000-0000-0000-0000-000000000000":
        add_general_regex_sanitizer(
            regex=transcription_subscription_id,
            value="00000000-0000-0000-0000-000000000000"
        )
    
    transcription_tenant_id = os.environ.get("TRANSCRIPTION_TENANT_ID", "")
    if transcription_tenant_id and transcription_tenant_id != "00000000-0000-0000-0000-000000000000":
        add_general_regex_sanitizer(
            regex=transcription_tenant_id,
            value="00000000-0000-0000-0000-000000000000"
        )
    
    transcription_client_id = os.environ.get("TRANSCRIPTION_CLIENT_ID", "")
    if transcription_client_id and transcription_client_id != "00000000-0000-0000-0000-000000000000":
        add_general_regex_sanitizer(
            regex=transcription_client_id,
            value="00000000-0000-0000-0000-000000000000"
        )
    
    transcription_client_secret = os.environ.get("TRANSCRIPTION_CLIENT_SECRET", "")
    if transcription_client_secret and transcription_client_secret != "00000000-0000-0000-0000-000000000000":
        add_general_regex_sanitizer(
            regex=transcription_client_secret,
            value="00000000-0000-0000-0000-000000000000"
        )

    # Sanitize endpoint URLs
    transcription_endpoint = os.environ.get(
        "TRANSCRIPTION_ENDPOINT", "https://fake-transcription-endpoint.cognitiveservices.azure.com/"
    )
    if transcription_endpoint and "fake" not in transcription_endpoint.lower():
        add_general_string_sanitizer(
            target=transcription_endpoint,
            value="https://fake-transcription-endpoint.cognitiveservices.azure.com/"
        )

    # Sanitize API keys in headers
    transcription_api_key = os.environ.get("TRANSCRIPTION_API_KEY", "fake-api-key")
    if transcription_api_key and transcription_api_key != "fake-api-key":
        add_header_regex_sanitizer(key="Ocp-Apim-Subscription-Key", value="fake-api-key")
        add_general_string_sanitizer(target=transcription_api_key, value="fake-api-key")

    # Sanitize authentication tokens
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    add_header_regex_sanitizer(key="Cookie", value="cookie;")
    add_header_regex_sanitizer(key="Authorization", value="Sanitized")
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")

    # Sanitize audio URLs in request/response bodies
    add_body_key_sanitizer(json_path="$..audioUrl", value="https://fake-audio-url.blob.core.windows.net/audio/test.wav")
    add_body_key_sanitizer(json_path="$..audio_url", value="https://fake-audio-url.blob.core.windows.net/audio/test.wav")

    # Sanitize storage account names and blob URLs
    add_uri_regex_sanitizer(
        regex=r"https://[a-z0-9]+\.blob\.core\.windows\.net",
        value="https://fakeaccount.blob.core.windows.net"
    )
    
    # Sanitize cognitive services hostnames to handle different endpoint formats
    # This handles both api.cognitive.microsoft.com and cognitiveservices.azure.com
    add_uri_regex_sanitizer(
        regex=r"https://[^/]+\.(api\.cognitive\.microsoft\.com|cognitiveservices\.azure\.com)",
        value="https://Sanitized.cognitiveservices.azure.com"
    )
