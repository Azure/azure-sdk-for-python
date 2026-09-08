# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import re
from unittest.mock import DEFAULT, patch

import pytest

import conftest


@pytest.fixture
def regex_sanitizers(monkeypatch, sanitized_values):
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "test-connection/gpt-5.4")
    monkeypatch.setenv("MODEL_DEPLOYMENT_NAME", "gpt-5.4")
    with patch.multiple(
        conftest,
        add_general_regex_sanitizer=DEFAULT,
        add_header_regex_sanitizer=DEFAULT,
        add_body_regex_sanitizer=DEFAULT,
        add_body_string_sanitizer=DEFAULT,
        add_body_key_sanitizer=DEFAULT,
        add_remove_header_sanitizer=DEFAULT,
        remove_batch_sanitizers=DEFAULT,
    ) as mocks:
        conftest.add_sanitizers.__wrapped__(None, sanitized_values)
        return [call.kwargs for call in mocks["add_general_regex_sanitizer"].call_args_list]


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
