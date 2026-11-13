# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from devtools_testutils import proxy_testcase
from devtools_testutils.aio import proxy_testcase_async
from devtools_testutils.preparers import AbstractPreparer

import test_operations as operations


@pytest.mark.parametrize("async_mode", [False, True])
def test_operations_load_service_credentials_before_client_creation(monkeypatch, async_mode):
    values = {"TENANT_ID": "test-tenant", "CLIENT_ID": "test-client", "CLIENT_SECRET": "test-secret"}
    for key, value in values.items():
        monkeypatch.setenv(f"PLATFORMVALIDATION_{key}", value)
        monkeypatch.setenv(f"AZURE_{key}", "unrelated-value")
    monkeypatch.setattr(operations.TestOperations, "is_live", True)
    monkeypatch.setattr(AbstractPreparer, "_resource_cache", {})
    monkeypatch.setattr(proxy_testcase, "is_live_and_not_recording", lambda: True)
    monkeypatch.setattr(proxy_testcase_async, "is_live_and_not_recording", lambda: True)
    credential = AsyncMock()
    credential_factory = Mock()

    def get_credential(*args, **kwargs):
        assert {key: os.environ[f"AZURE_{key}"] for key in values} == values
        credential_factory(*args, **kwargs)
        return credential

    client = MagicMock()
    client.__enter__.return_value = client
    client.__aenter__.return_value = client
    if async_mode:

        async def entries():
            for entry in []:
                yield entry

        client.operations.list.side_effect = entries
    else:
        client.operations.list.return_value = []
    checked = Mock()
    monkeypatch.setattr(operations, "assert_operations", checked)
    case = operations.TestOperations()
    monkeypatch.setattr(case, "get_settings_value", lambda _: "test-subscription")
    monkeypatch.setattr(case, "get_credential", get_credential)
    monkeypatch.setattr(case, "create_client_from_credential", lambda *args, **kwargs: client)
    if async_mode:
        case.test_list_management_operations_async()
        credential.close.assert_awaited_once()
    else:
        case.test_list_management_operations()
    credential_factory.assert_called_once()
    checked.assert_called_once_with([])
