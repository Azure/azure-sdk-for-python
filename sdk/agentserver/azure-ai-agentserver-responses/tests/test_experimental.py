# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging

import pytest

from azure.ai.agentserver.core import experimental
from azure.ai.agentserver.core._experimental import (
    DISABLE_EXPERIMENTAL_WARNING_ENV_VAR,
    EXPERIMENTAL_CLASS_MESSAGE,
    _warning_cache,
)
from azure.ai.agentserver.responses import FoundryStorageSettings, ResponsesAgentServerHost
from azure.ai.agentserver.responses.store import _foundry_errors, _foundry_provider, _foundry_settings


def test_foundry_storage_settings_is_experimental(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        FoundryStorageSettings.from_endpoint("https://example.foundry.azure.com")

    assert FoundryStorageSettings.__doc__.startswith(".. note::")
    assert EXPERIMENTAL_CLASS_MESSAGE in FoundryStorageSettings.__doc__
    assert len(caplog.records) == 1
    assert EXPERIMENTAL_CLASS_MESSAGE in caplog.records[0].message
    assert caplog.records[0].message.endswith("This is an experimental class, and may change at any time.")
    assert "https://" not in FoundryStorageSettings.__doc__


@pytest.mark.parametrize("module", [_foundry_errors, _foundry_provider, _foundry_settings])
def test_storage_modules_use_core_experimental_decorator(module) -> None:
    assert module.experimental is experimental


def test_storage_experimental_warnings_are_deduplicated(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        FoundryStorageSettings.from_endpoint("https://example.foundry.azure.com")
        FoundryStorageSettings.from_endpoint("https://example.foundry.azure.com")

    assert len(caplog.records) == 1
    assert caplog.records[0].name == "azure.ai.agentserver.core._experimental"


def test_storage_experimental_warnings_can_be_suppressed(monkeypatch, caplog) -> None:
    _warning_cache.clear()
    monkeypatch.setenv(DISABLE_EXPERIMENTAL_WARNING_ENV_VAR, "true")

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        FoundryStorageSettings.from_endpoint("https://example.foundry.azure.com")

    assert len(caplog.records) == 0


def test_protocol_hosts_are_not_marked_experimental() -> None:
    assert not ResponsesAgentServerHost.__doc__.startswith(".. note::")
