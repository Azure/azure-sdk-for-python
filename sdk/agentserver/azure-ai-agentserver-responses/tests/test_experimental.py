# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging

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


def test_protocol_hosts_are_not_marked_experimental() -> None:
    assert not ResponsesAgentServerHost.__doc__.startswith(".. note::")
