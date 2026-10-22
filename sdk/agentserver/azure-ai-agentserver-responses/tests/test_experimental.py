# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import importlib.util
import logging
from unittest.mock import patch

import pytest

from azure.ai.agentserver.responses import _experimental as experimental_module
from azure.ai.agentserver.responses import FoundryStorageSettings, ResponsesAgentServerHost
from azure.ai.agentserver.responses._experimental import EXPERIMENTAL_CLASS_MESSAGE, _warning_cache, experimental


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


@pytest.mark.parametrize("kind", ["class", "method"])
def test_fallback_experimental_warning_has_no_link(kind, caplog) -> None:
    spec = importlib.util.spec_from_file_location("fallback_experimental", experimental_module.__file__)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    with patch("importlib.import_module", side_effect=ImportError):
        spec.loader.exec_module(module)

    if kind == "class":

        @module.experimental
        class ExperimentalClass:
            def __init__(self) -> None:
                self.value = 1

        wrapped = ExperimentalClass
    else:

        @module.experimental
        def experimental_function() -> bool:
            return True

        wrapped = experimental_function

    with caplog.at_level(logging.WARNING, logger=module.__name__):
        wrapped()

    assert len(caplog.records) == 1
    assert caplog.records[0].message.endswith(f"This is an experimental {kind}, and may change at any time.")
    assert "https://" not in wrapped.__doc__


def test_protocol_hosts_are_not_marked_experimental() -> None:
    assert not ResponsesAgentServerHost.__doc__.startswith(".. note::")
