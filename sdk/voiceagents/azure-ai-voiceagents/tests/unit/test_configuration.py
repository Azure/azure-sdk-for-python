# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for VoiceAgentsClientConfiguration defaults. No network calls."""
import pytest

from azure.ai.voiceagents._configuration import VoiceAgentsClientConfiguration

ENDPOINT = "https://example.services.ai.azure.com/api/projects/p"


class _FakeCredential:
    def get_token(self, *scopes, **kwargs):
        raise NotImplementedError


def test_default_api_version_is_v1():
    config = VoiceAgentsClientConfiguration(endpoint=ENDPOINT, credential=_FakeCredential())
    assert config.api_version == "v1"


def test_default_credential_scopes():
    config = VoiceAgentsClientConfiguration(endpoint=ENDPOINT, credential=_FakeCredential())
    assert config.credential_scopes == ["https://ai.azure.com/.default"]


def test_endpoint_and_credential_are_saved():
    credential = _FakeCredential()
    config = VoiceAgentsClientConfiguration(endpoint=ENDPOINT, credential=credential)
    assert config.endpoint == ENDPOINT
    assert config.credential is credential


def test_endpoint_is_required():
    with pytest.raises(ValueError):
        VoiceAgentsClientConfiguration(endpoint=None, credential=_FakeCredential())


def test_credential_is_required():
    with pytest.raises(ValueError):
        VoiceAgentsClientConfiguration(endpoint=ENDPOINT, credential=None)


def test_api_version_can_be_overridden():
    config = VoiceAgentsClientConfiguration(endpoint=ENDPOINT, credential=_FakeCredential(), api_version="v1")
    assert config.api_version == "v1"
