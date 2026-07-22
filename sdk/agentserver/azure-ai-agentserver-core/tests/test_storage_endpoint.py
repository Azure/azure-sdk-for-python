# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for FoundryStorageEndpoint resolution and URL building."""

from __future__ import annotations

import pytest
from azure.ai.agentserver.core.storage import FoundryStorageEndpoint


def test_from_endpoint_derives_storage_base_url() -> None:
    ep = FoundryStorageEndpoint.from_endpoint("https://proj.example.com/api/projects/p")
    assert ep.storage_base_url == "https://proj.example.com/api/projects/p/storage/"
    assert ep.api_version == "v1"


def test_from_endpoint_strips_trailing_slash() -> None:
    ep = FoundryStorageEndpoint.from_endpoint("https://proj.example.com/")
    assert ep.storage_base_url == "https://proj.example.com/storage/"


def test_from_endpoint_accepts_storage_base_url() -> None:
    ep = FoundryStorageEndpoint.from_endpoint("https://proj.example.com/storage/")
    assert ep.storage_base_url == "https://proj.example.com/storage/"


def test_from_endpoint_rejects_empty() -> None:
    with pytest.raises(ValueError):
        FoundryStorageEndpoint.from_endpoint("")


def test_from_endpoint_rejects_non_absolute() -> None:
    with pytest.raises(ValueError):
        FoundryStorageEndpoint.from_endpoint("proj.example.com")


def test_from_env_reads_project_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://proj.example.com")
    ep = FoundryStorageEndpoint.from_env()
    assert ep.storage_base_url == "https://proj.example.com/storage/"


def test_from_env_requires_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FOUNDRY_PROJECT_ENDPOINT", raising=False)
    with pytest.raises(EnvironmentError):
        FoundryStorageEndpoint.from_env()


def test_build_url_appends_api_version() -> None:
    ep = FoundryStorageEndpoint(storage_base_url="https://x/storage/", api_version="v1")
    assert ep.build_url("state_stores") == "https://x/storage/state_stores?api-version=v1"


def test_build_url_appends_extra_params_encoded() -> None:
    ep = FoundryStorageEndpoint(storage_base_url="https://x/storage/", api_version="v1")
    url = ep.build_url("state_stores", after="it 1/2")
    assert url == "https://x/storage/state_stores?api-version=v1&after=it%201%2F2"
