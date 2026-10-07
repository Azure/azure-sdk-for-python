# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import re
from unittest.mock import MagicMock, patch

import pytest

from agent_insights import sanitizers


@pytest.fixture(name="sanitizer_calls")
def _sanitizer_calls(monkeypatch, sanitized_values, sanitizer_configuration):
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "test-connection/gpt-5.4")
    monkeypatch.setenv("MODEL_DEPLOYMENT_NAME", "gpt-5.4")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "test-connection/gpt-5.4-agent")
    mocks = {
        name: MagicMock()
        for name in (
            "add_general_regex_sanitizer",
            "add_header_regex_sanitizer",
            "add_body_regex_sanitizer",
            "add_body_string_sanitizer",
            "add_body_key_sanitizer",
            "add_remove_header_sanitizer",
            "remove_batch_sanitizers",
        )
    }
    with patch.dict(sanitizer_configuration.__globals__, mocks), patch.dict(sanitizers.__dict__, mocks):
        sanitizer_configuration(None, sanitized_values)
    return mocks


@pytest.fixture(name="regex_sanitizers")
def _regex_sanitizers(sanitizer_calls):
    return [call.kwargs for call in sanitizer_calls["add_general_regex_sanitizer"].call_args_list]


def test_recordings_remove_private_response_headers(sanitizer_calls):
    headers = {
        header.strip()
        for call in sanitizer_calls["add_remove_header_sanitizer"].call_args_list
        for header in call.kwargs["headers"].split(",")
    }
    assert {"azureml-served-by-cluster", "openai-organization", "openai-project"} <= headers


@pytest.mark.parametrize(
    "prefix,hex_length,placeholder",
    [
        ("monitor_", 32, "monitor_" + "0" * 32),
        ("run_", 32, "run_" + "0" * 32),
        ("insight_", 32, "insight_" + "0" * 24),
    ],
)
def test_agent_insights_ids_do_not_change_other_id_types(regex_sanitizers, prefix, hex_length, placeholder):
    pattern = next(rule["regex"] for rule in regex_sanitizers if rule["value"] == placeholder)
    identifier = prefix + "a" * hex_length

    assert re.sub(pattern, placeholder, f"/{identifier}?api-version=v1") == f"/{placeholder}?api-version=v1"
    assert re.sub(pattern, placeholder, f"eval{identifier}") == f"eval{identifier}"
    assert re.sub(pattern, placeholder, f'"parent_{identifier}"') == f'"parent_{identifier}"'


def test_qualified_model_name_is_sanitized_before_its_suffix(regex_sanitizers, sanitized_values):
    placeholder = sanitized_values["model_deployment_name"]
    value = "test-connection/gpt-5.4"
    for rule in regex_sanitizers:
        if rule["value"] == placeholder:
            value = re.sub(rule["regex"], placeholder, value)
    assert value == placeholder


@pytest.mark.parametrize("sanitizer_name", ["add_general_regex_sanitizer", "add_body_string_sanitizer"])
def test_agent_name_is_sanitized_before_its_model_prefix(sanitizer_calls, sanitized_values, sanitizer_name):
    value = "test-connection/gpt-5.4-agent"
    for call in sanitizer_calls[sanitizer_name].call_args_list:
        rule = call.kwargs
        if sanitizer_name == "add_general_regex_sanitizer":
            value = re.sub(rule["regex"], rule["value"], value)
        else:
            value = value.replace(rule["target"], rule["value"])
    assert value == sanitized_values["agent_name"]


def test_sample_sanitizers_are_scoped_and_preserve_random_trace_relationships(monkeypatch):
    mocks = {
        name: MagicMock()
        for name in ("add_general_regex_sanitizer", "add_body_key_sanitizer", "add_header_regex_sanitizer")
    }
    for name, mock in mocks.items():
        monkeypatch.setattr(sanitizers, name, mock)
    generator = sanitizers.RandomIdGenerator()
    with sanitizers.agent_insights_sample_sanitizers():
        trace_ids = [generator.generate_trace_id() for _ in range(2)]
        span_ids = [generator.generate_span_id() for _ in range(3)]

    for mock in mocks.values():
        assert all(call.kwargs["function_scoped"] for call in mock.call_args_list)
    id_rules = [
        call.kwargs
        for call in mocks["add_general_regex_sanitizer"].call_args_list
        if call.kwargs.get("condition", {}).get("uriRegex", "").endswith("/track")
    ]
    assert len(id_rules) == 5
    for identifiers, width, rules in ((trace_ids, 32, id_rules[:2]), (span_ids, 16, id_rules[2:])):
        assert len(set(identifiers)) == len(identifiers)
        for index, (identifier, rule) in enumerate(zip(identifiers, rules), 1):
            assert identifier != index
            assert re.sub(rule["regex"], rule["value"], f"{identifier:0{width}x}") == f"{index:0{width}x}"

    connection_rules = [
        call.kwargs
        for call in mocks["add_body_key_sanitizer"].call_args_list
        if "ConnectionString" in call.kwargs["json_path"] or "credentials.key" in call.kwargs["json_path"]
    ]
    assert len(connection_rules) == 2
    for rule in connection_rules:
        assert re.search(
            rule["condition"]["uriRegex"], "https://example.com/connections/name/getConnectionWithCredentials"
        )
        assert not re.search(rule["condition"]["uriRegex"], "https://example.com/agent_insight_monitors")
        assert "InstrumentationKey=00000000-0000-0000-0000-000000000000;" in rule["value"]

    context_rule = mocks["add_header_regex_sanitizer"].call_args.kwargs
    assert context_rule["key"] == "Request-Context"
    for prefix in ("appId=", "appId=cid-v1:"):
        identifier = "12345678-1234-1234-1234-123456789012"
        match = re.search(context_rule["regex"], prefix + identifier)
        assert match is not None
        assert match.group(int(context_rule["group_for_replace"])) == identifier
