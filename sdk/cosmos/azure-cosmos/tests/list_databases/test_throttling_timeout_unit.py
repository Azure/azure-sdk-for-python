# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Check configured authentication and throttling evidence for database listing."""

from unittest.mock import Mock

import pytest

from config import clients
from config.settings import TestSettings
from list_databases._throttling_timeout import assert_throttled_timeout
from list_databases.aio import test_throttling_timeout_async as async_tests
from list_databases.sync import test_throttling_timeout as sync_tests


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("auth", ["key", "aad"])
async def test_throttling_listing_uses_configured_authentication_rust(monkeypatch, asynchronous, auth):
    monkeypatch.setattr(TestSettings, "host", "https://account.example.invalid/")
    monkeypatch.setattr(TestSettings, "masterKey", "test-key")
    monkeypatch.setattr(TestSettings, "data_auth_mode", auth)
    monkeypatch.setattr(TestSettings, "is_emulator", False)
    credential = object()
    credential_factory = Mock(return_value=credential)
    monkeypatch.setattr(clients, "_aad_credential", credential_factory)
    constructor = Mock()

    class ClientSelected(Exception):
        pass

    def capture_client(self, endpoint, selected_credential, **kwargs):
        constructor(endpoint, selected_credential, **kwargs)
        raise ClientSelected

    client_class = clients.AsyncCosmosClient if asynchronous else clients.CosmosClient
    monkeypatch.setattr(client_class, "__init__", capture_client)
    with pytest.raises(ClientSelected):
        if asynchronous:
            await async_tests.TestCRUDOperationsAsync().test_timeout_on_throttling_error_async_rust()
        else:
            sync_tests.TestCRUDOperations().test_timeout_on_throttling_error_rust()

    constructor.assert_called_once()
    assert constructor.call_args.args == (
        TestSettings.host, credential if auth == "aad" else TestSettings.masterKey,
    )
    assert constructor.call_args.kwargs["_backend"] == "rust"
    assert constructor.call_args.kwargs["_fault_injection_rules"]
    if auth == "aad":
        credential_factory.assert_called_once_with(asynchronous)
    else:
        credential_factory.assert_not_called()


@pytest.mark.parametrize("timeout", [29, 12])
def test_throttling_timeout_assertions_accept_retries_at_the_deadline_rust(timeout):
    assert_throttled_timeout((0, 4), (timeout, 7), timeout)


@pytest.mark.parametrize("timeout", [29, 12])
@pytest.mark.parametrize("failure", ["no-retry", "early", "late"])
def test_throttling_timeout_assertions_reject_incomplete_evidence_rust(timeout, failure):
    elapsed = timeout - 2 if failure == "early" else timeout + 5 if failure == "late" else timeout
    hits = 1 if failure == "no-retry" else 3
    with pytest.raises(AssertionError):
        assert_throttled_timeout((0, 4), (elapsed, 4 + hits), timeout)
