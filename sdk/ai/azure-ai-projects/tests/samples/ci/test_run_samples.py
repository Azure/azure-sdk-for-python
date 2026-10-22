# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Offline checks for the live sample-test invocation contract."""

from copy import deepcopy
from pathlib import Path

import pytest

from run_samples import build_command


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
