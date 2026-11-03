# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Offline regression of CLI-mode conftest configuration without loading service fixtures."""

import ast
import json
import os
from pathlib import Path
import sys
import re
from types import SimpleNamespace

import pytest


@pytest.fixture(autouse=True)
def isolated_configuration_environment(monkeypatch):
    monkeypatch.delenv("AZURE_AI_PROJECTS_TEST_ENVIRONMENT_NAMES", raising=False)
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "fixture-model")
    monkeypatch.setenv("LLM_VALIDATION_PROJECT_ENDPOINT", "fixture-endpoint")


def load_cli_environment_hooks():
    """Load the real option registry and hooks without importing proxy fixtures or dotenv."""
    path = Path(__file__).resolve().parents[2] / "conftest.py"
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    hooks = [
        node
        for node in module.body
        if (
            isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "_CLI_ENV_OPTIONS" for target in node.targets)
        )
        or (
            isinstance(node, ast.FunctionDef)
            and node.name
            in {"_get_ci_environment_options", "_has_cli_env_options", "pytest_addoption", "pytest_configure"}
        )
    ]
    namespace = {
        "os": os,
        "sys": sys,
        "json": json,
        "re": re,
        "_CLI_ENV_MODE": True,
        "_SERVICE_PREPARER_DEFAULTS": {
            "llm_validation_project_endpoint": "https://sanitized.services.ai.azure.com/api/projects/sanitized",
            "foundry_model_name": "sanitized-model",
        },
    }
    exec(compile(ast.Module(body=hooks, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def test_future_resource_binding_is_registered_without_a_python_option_mapping(monkeypatch):
    monkeypatch.setenv("AZURE_AI_PROJECTS_TEST_ENVIRONMENT_NAMES", '["NEW_RESOURCE_ENDPOINT"]')
    hooks = load_cli_environment_hooks()
    parser = pytest.Parser(_ispytest=True)
    hooks["pytest_addoption"](parser)
    options = vars(parser.parse(["--new-resource-endpoint=https://example.invalid/new"]))
    hooks["pytest_configure"](SimpleNamespace(getoption=options.get))
    assert os.environ["NEW_RESOURCE_ENDPOINT"] == "https://example.invalid/new"


@pytest.mark.parametrize("names", ['["ACCESS_TOKEN"]', '["lowercase"]', '{"NAME": "value"}', "[123]", "not-json"])
def test_invalid_dynamic_option_names_fail_explicitly(monkeypatch, names):
    monkeypatch.setenv("AZURE_AI_PROJECTS_TEST_ENVIRONMENT_NAMES", names)
    with pytest.raises(ValueError):
        load_cli_environment_hooks()


def configure_cli_environment(values):
    namespace = load_cli_environment_hooks()
    namespace["pytest_configure"](SimpleNamespace(getoption=values.get))


@pytest.mark.parametrize("separator", ["-", "_"])
def test_function_cli_options_are_registered_and_applied(separator, monkeypatch):
    hooks = load_cli_environment_hooks()
    parser = pytest.Parser(_ispytest=True)
    hooks["pytest_addoption"](parser)
    environment = {
        "FUNCTION_APP_NAME": "example-function",
        "FUNCTION_APP_URL": "https://example-function.azurewebsites.net",
        "STORAGE_INPUT_QUEUE_NAME": "weather-input-queue",
        "STORAGE_OUTPUT_QUEUE_NAME": "weather-output-queue",
        "STORAGE_QUEUE_SERVICE_ENDPOINT": "https://example.queue.core.windows.net",
    }
    arguments = [f"--{name.lower().replace('_', separator)}={value}" for name, value in environment.items()]
    for name in environment:
        monkeypatch.setenv(name, "old-value")
    monkeypatch.setattr(sys, "argv", ["pytest", *arguments])
    assert hooks["_has_cli_env_options"]()
    options = vars(parser.parse(arguments))
    hooks["pytest_configure"](SimpleNamespace(getoption=options.get))
    for name, value in environment.items():
        assert os.environ[name] == value


def test_secret_endpoint_is_not_overwritten_by_preparer_default(monkeypatch):
    endpoint = "https://external-validator.services.ai.azure.com/api/projects/validator"
    monkeypatch.setenv("LLM_VALIDATION_PROJECT_ENDPOINT", endpoint)
    configure_cli_environment({"foundry_model_name": "gpt-4.1"})
    assert os.environ["LLM_VALIDATION_PROJECT_ENDPOINT"] == endpoint
    assert os.environ["FOUNDRY_MODEL_NAME"] == "gpt-4.1"


def test_explicit_local_cli_option_still_has_precedence(monkeypatch):
    monkeypatch.setenv("LLM_VALIDATION_PROJECT_ENDPOINT", "existing-env-value")
    configure_cli_environment({"llm_validation_project_endpoint": "explicit-cli-value"})
    assert os.environ["LLM_VALIDATION_PROJECT_ENDPOINT"] == "explicit-cli-value"


def test_playback_default_remains_available_without_secret(monkeypatch):
    monkeypatch.delenv("LLM_VALIDATION_PROJECT_ENDPOINT", raising=False)
    configure_cli_environment({})
    assert (
        os.environ["LLM_VALIDATION_PROJECT_ENDPOINT"]
        == "https://sanitized.services.ai.azure.com/api/projects/sanitized"
    )


def test_other_unspecified_options_still_use_preparer_defaults():
    configure_cli_environment({})
    assert os.environ["FOUNDRY_MODEL_NAME"] == "sanitized-model"
