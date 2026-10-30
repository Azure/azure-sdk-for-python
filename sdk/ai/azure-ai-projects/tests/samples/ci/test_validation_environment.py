# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Offline regression of CLI-mode conftest configuration without loading service fixtures."""

import ast
import os
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture(autouse=True)
def isolated_configuration_environment(monkeypatch):
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "fixture-model")
    monkeypatch.setenv("LLM_VALIDATION_PROJECT_ENDPOINT", "fixture-endpoint")


def configure_cli_environment(values):
    """Execute the actual configure hook in isolation, without importing proxy fixtures or dotenv."""
    path = Path(__file__).resolve().parents[2] / "conftest.py"
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    hook = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "pytest_configure")
    namespace = {
        "os": os,
        "_CLI_ENV_MODE": True,
        "_CLI_ENV_OPTIONS": {
            "llm_validation_project_endpoint": "LLM_VALIDATION_PROJECT_ENDPOINT",
            "foundry_model_name": "FOUNDRY_MODEL_NAME",
        },
        "_SERVICE_PREPARER_DEFAULTS": {
            "llm_validation_project_endpoint": "https://sanitized.services.ai.azure.com/api/projects/sanitized",
            "foundry_model_name": "sanitized-model",
        },
    }
    exec(compile(ast.Module(body=[hook], type_ignores=[]), str(path), "exec"), namespace)
    namespace["pytest_configure"](SimpleNamespace(getoption=values.get))


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
