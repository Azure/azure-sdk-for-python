# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Offline checks for the live sample-test invocation contract."""

from contextlib import nullcontext
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import run_samples
from run_samples import build_command, wait_for_project


def ready_state():
    return {
        "schemaVersion": 1,
        "status": "Ready",
        "plan": {
            "selectedTests": [
                {"node_id": "tests/samples/test_samples.py::TestSamples::test_agent_tools_samples[sample_mcp]"}
            ]
        },
        "environment": {
            "FOUNDRY_PROJECT_ENDPOINT": "https://example.services.ai.azure.com/api/projects/test",
            "FOUNDRY_MODEL_NAME": "gpt-4.1",
            "FOUNDRY_AGENT_NAME": "sample-test",
            "LLM_VALIDATION_PROJECT_ENDPOINT": "https://example.services.ai.azure.com/api/projects/test",
            "MCP_PROJECT_CONNECTION_ID": "/subscriptions/example/connections/mcp",
            "AZURE_SUBSCRIPTION_ID": "00000000-0000-0000-0000-000000000000",
            "AZURE_RESOURCE_GROUP": "example-ci-group",
        },
    }


def test_command_executes_pytest_live_without_recording():
    state = ready_state()
    original = deepcopy(state)
    command = build_command(state, Path("results.xml"))
    assert command[1:3] == ["-m", "pytest"]
    assert state["plan"]["selectedTests"][0]["node_id"] in command
    assert "--azure-test-run-live=true" in command
    assert "--azure-skip-live-recording=true" in command
    assert "--foundry-model-name=gpt-4.1" in command
    assert "--llm-validation-project-endpoint=" + state["environment"]["LLM_VALIDATION_PROJECT_ENDPOINT"] in command
    assert "--mcp-project-connection-id=/subscriptions/example/connections/mcp" in command
    assert state == original


@pytest.mark.parametrize("status", ["Provisioning", "CleanedUp", "Failed", None])
def test_incomplete_provisioning_is_rejected(status):
    state = ready_state()
    state["status"] = status
    with pytest.raises(ValueError, match="provisioning must complete"):
        build_command(state, Path("results.xml"))


def test_no_tests_never_falls_back_to_running_everything():
    state = ready_state()
    state["plan"]["selectedTests"] = []
    with pytest.raises(ValueError, match="Only collected"):
        build_command(state, Path("results.xml"))


@pytest.mark.parametrize("node", ["tests/test_base.py", "-k", "--collect-only", "test_anything", "test\nnext"])
def test_nodes_cannot_be_pytest_options_or_other_tests(node):
    state = ready_state()
    state["plan"]["selectedTests"][0]["node_id"] = node
    with pytest.raises(ValueError, match="Only collected"):
        build_command(state, Path("results.xml"))


def test_async_sample_node_is_preserved():
    state = ready_state()
    node = "tests/samples/test_samples_async.py::TestSamplesAsync::test_agent_tools_samples_async[sample_mcp_async]"
    state["plan"]["selectedTests"][0]["node_id"] = node
    assert node in build_command(state, Path("results.xml"))


@pytest.mark.parametrize("key", ["MCP_GITHUB_PAT", "PROJ_CONN_MCP_KEY", "UNKNOWN_SETTING"])
def test_unexpected_or_secret_bindings_cannot_become_cli_options(key):
    state = ready_state()
    state["environment"][key] = "do-not-log-this"
    with pytest.raises(ValueError, match="only the expected non-secret"):
        build_command(state, Path("results.xml"))


def test_optional_mcp_binding_can_be_absent():
    state = ready_state()
    del state["environment"]["MCP_PROJECT_CONNECTION_ID"]
    assert not any("mcp-project-connection-id" in argument for argument in build_command(state, Path("results.xml")))


def test_mcp_selection_requires_connection_output():
    state = ready_state()
    state["plan"]["provisionMcp"] = True
    state["environment"]["MCP_PROJECT_CONNECTION_ID"] = ""
    with pytest.raises(ValueError, match="nonempty MCP_PROJECT_CONNECTION_ID"):
        build_command(state, Path("results.xml"))


@pytest.fixture
def readiness_probe(monkeypatch):
    import azure.ai.projects
    import azure.identity

    client = SimpleNamespace(agents=SimpleNamespace(list=Mock(return_value=iter(()))))
    monkeypatch.setattr(azure.identity, "AzureCliCredential", lambda: nullcontext(object()))
    monkeypatch.setattr(azure.ai.projects, "AIProjectClient", lambda *_args: nullcontext(client))
    clock = [0.0]
    monkeypatch.setattr(run_samples.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(run_samples.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds))
    return client, clock


def readiness_error(status, code, message):
    from azure.core.exceptions import HttpResponseError

    response = Mock(status_code=status, reason="Readiness error")
    response.text.return_value = json.dumps({"error": {"code": code, "message": message}})
    return HttpResponseError(response=response)


AGENT_INDEX_TIMEOUT = (
    "Listing agents timed out after 8s while reading the agent index. "
    "This usually indicates the project's bring-your-own Cosmos DB endpoint is unreachable or misconfigured."
)


def test_agent_index_timeout_is_retried_before_sample_starts(readiness_probe, capsys):
    client, clock = readiness_probe
    error = readiness_error(400, "invalid_configuration", AGENT_INDEX_TIMEOUT)
    client.agents.list.side_effect = [error, iter(())]
    wait_for_project("https://example.services.ai.azure.com/api/projects/test", timeout=30)
    assert client.agents.list.call_count == 2
    assert clock[0] == 10
    assert "agent-index-timeout" in capsys.readouterr().out


@pytest.mark.parametrize("status", [403, 404, 409, 429, 500, 502, 503, 504])
def test_existing_propagation_errors_are_still_retried(readiness_probe, status):
    client, _ = readiness_probe
    client.agents.list.side_effect = [readiness_error(status, "Pending", "Not ready"), iter(())]
    wait_for_project("https://example.services.ai.azure.com/api/projects/test", timeout=30)
    assert client.agents.list.call_count == 2


@pytest.mark.parametrize(
    "status,code,message",
    [
        (400, "invalid_configuration", "The Cosmos DB connection is missing."),
        (400, "invalid_configuration", "Invalid model configuration."),
        (400, "BadRequest", AGENT_INDEX_TIMEOUT),
        (401, "Unauthorized", "Credentials are invalid."),
    ],
)
def test_unrelated_configuration_and_authentication_errors_fail_fast(readiness_probe, status, code, message):
    client, clock = readiness_probe
    error = readiness_error(status, code, message)
    client.agents.list.side_effect = error
    with pytest.raises(type(error)) as failure:
        wait_for_project("https://example.services.ai.azure.com/api/projects/test", timeout=30)
    assert failure.value is error
    assert client.agents.list.call_count == 1
    assert clock[0] == 0


def test_persistent_agent_index_timeout_is_bounded_and_does_not_start_pytest(readiness_probe, monkeypatch):
    client, clock = readiness_probe
    client.agents.list.side_effect = readiness_error(400, "invalid_configuration", AGENT_INDEX_TIMEOUT)
    sample_process = Mock(side_effect=AssertionError("Samples must not run before readiness succeeds."))
    monkeypatch.setattr(run_samples.subprocess, "run", sample_process)
    with pytest.raises(TimeoutError, match="Project readiness did not succeed"):
        wait_for_project("https://example.services.ai.azure.com/api/projects/test", timeout=15)
    assert client.agents.list.call_count == 2
    assert clock[0] == 15
    sample_process.assert_not_called()


def test_readiness_probe_limits_the_read_request(readiness_probe):
    client, _ = readiness_probe
    wait_for_project("https://example.services.ai.azure.com/api/projects/test")
    client.agents.list.assert_called_once_with(limit=1, connection_timeout=10, read_timeout=30, retry_total=0)
