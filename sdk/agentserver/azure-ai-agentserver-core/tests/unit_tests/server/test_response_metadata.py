# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json

from azure.ai.agentserver.core.application import PackageMetadata, get_current_app, set_current_app
from azure.ai.agentserver.core.models import Response as OpenAIResponse
from azure.ai.agentserver.core.models.projects import ResponseCreatedEvent, ResponseErrorEvent
from azure.ai.agentserver.core.server._response_metadata import (
    METADATA_KEY,
    attach_foundry_metadata_to_response,
    build_foundry_agents_metadata_headers,
    try_attach_foundry_metadata_to_event,
)


def _set_test_app() -> PackageMetadata:
    previous = get_current_app()
    set_current_app(
        PackageMetadata(
            name="test-package",
            version="1.2.3",
            python_version="3.11.0",
            platform="test-platform",
        )
    )
    return previous


def _expected_payload() -> dict[str, str]:
    return {
        "name": "test-package",
        "version": "1.2.3",
        "python_version": "3.11.0",
        "platform": "test-platform",
    }


def test_build_foundry_agents_metadata_headers_returns_json():
    previous = _set_test_app()
    try:
        headers = build_foundry_agents_metadata_headers()
        payload = json.loads(headers["x-aml-foundry-agents-metadata"])
        assert payload == _expected_payload()
    finally:
        set_current_app(previous)


def test_attach_foundry_metadata_to_response_sets_metadata_key():
    previous = _set_test_app()
    try:
        response = OpenAIResponse({"object": "response", "id": "resp", "metadata": {}})
        attach_foundry_metadata_to_response(response)
        assert METADATA_KEY in response.metadata
        assert json.loads(response.metadata[METADATA_KEY]) == _expected_payload()
    finally:
        set_current_app(previous)


def test_try_attach_foundry_metadata_to_event_attaches_for_supported_events():
    previous = _set_test_app()
    try:
        response = OpenAIResponse({"object": "response", "id": "resp", "metadata": {}})
        event = ResponseCreatedEvent({"sequence_number": 0, "response": response})
        try_attach_foundry_metadata_to_event(event)
        assert METADATA_KEY in response.metadata

        unsupported = ResponseErrorEvent(
            {"sequence_number": 1, "code": "server_error", "message": "boom", "param": ""}
        )
        try_attach_foundry_metadata_to_event(unsupported)
    finally:
        set_current_app(previous)
