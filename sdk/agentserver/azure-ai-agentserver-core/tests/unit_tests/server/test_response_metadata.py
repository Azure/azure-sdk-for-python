# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json

from azure.ai.agentserver.core.application import (
    PackageMetadata,
    RuntimeMetadata,
    get_current_app,
    set_current_app,
)
from azure.ai.agentserver.core.models import Response as OpenAIResponse
from azure.ai.agentserver.core.models.projects import ResponseCreatedEvent, ResponseErrorEvent
from azure.ai.agentserver.core.server._response_metadata import (
    METADATA_KEY,
    attach_foundry_metadata_to_response,
    build_foundry_agents_metadata_headers,
    try_attach_foundry_metadata_to_event,
)


def _set_test_app():
    previous = get_current_app()
    set_current_app(
        PackageMetadata(
            name="test-package",
            version="1.2.3",
        ),
        RuntimeMetadata(
            python_version="3.11.0",
            platform="test-platform",
            host_name="test-host",
            replica_name="test-replica",
        ),
    )
    return previous


def _expected_payload() -> dict[str, dict[str, str]]:
    return {
        "package": {
            "name": "test-package",
            "version": "1.2.3",
        },
        "runtime": {
            "python_version": "3.11.0",
            "platform": "test-platform",
            "host_name": "test-host",
            "replica_name": "test-replica",
        },
    }


def test_build_foundry_agents_metadata_headers_returns_json():
    previous = _set_test_app()
    try:
        headers = build_foundry_agents_metadata_headers()
        payload = json.loads(headers["x-aml-foundry-agents-metadata"])
        assert payload == _expected_payload()
    finally:
        set_current_app(previous.package, previous.runtime)


def test_attach_foundry_metadata_to_response_sets_metadata_key():
    previous = _set_test_app()
    try:
        response = OpenAIResponse({"object": "response", "id": "resp", "metadata": {}})
        attach_foundry_metadata_to_response(response)
        assert METADATA_KEY in response.metadata
        assert json.loads(response.metadata[METADATA_KEY]) == _expected_payload()
    finally:
        set_current_app(previous.package, previous.runtime)


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
        set_current_app(previous.package, previous.runtime)


def test_runtime_metadata_merge_overrides_non_empty_fields():
    base = RuntimeMetadata(
        python_version="3.10.0",
        platform="base-platform",
        host_name="base-host",
        replica_name="base-replica",
    )
    override = RuntimeMetadata(
        python_version="",
        platform="override-platform",
        host_name="",
        replica_name="override-replica",
    )

    merged = base.merged_with(override)

    assert merged.python_version == "3.10.0"
    assert merged.platform == "override-platform"
    assert merged.host_name == "base-host"
    assert merged.replica_name == "override-replica"


def test_runtime_metadata_resolve_falls_back_when_env_missing(monkeypatch):
    monkeypatch.delenv("CONTAINER_APP_REVISION_FQDN", raising=False)
    monkeypatch.delenv("CONTAINER_APP_REPLICA_NAME", raising=False)
    runtime = RuntimeMetadata.resolve()

    assert runtime.host_name == ""
    assert runtime.replica_name == ""
    assert runtime.python_version
    assert runtime.platform


def test_runtime_metadata_resolve_aca_env(monkeypatch):
    monkeypatch.setenv("CONTAINER_APP_REVISION_FQDN", "aca-host")
    monkeypatch.setenv("CONTAINER_APP_REPLICA_NAME", "aca-replica")
    runtime = RuntimeMetadata.resolve()

    assert runtime.host_name == "aca-host"
    assert runtime.replica_name == "aca-replica"


def test_runtime_metadata_resolve_explicit_overrides(monkeypatch):
    monkeypatch.setenv("CONTAINER_APP_REVISION_FQDN", "aca-host")
    monkeypatch.setenv("CONTAINER_APP_REPLICA_NAME", "aca-replica")

    runtime = RuntimeMetadata.resolve(host_name="override-host", replica_name="override-replica")

    assert runtime.host_name == "override-host"
    assert runtime.replica_name == "override-replica"
