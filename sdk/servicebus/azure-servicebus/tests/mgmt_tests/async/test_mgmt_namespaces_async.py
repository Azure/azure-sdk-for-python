# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from azure.servicebus.aio.management import ServiceBusAdministrationClient

from devtools_testutils import AzureMgmtRecordedTestCase, get_credential
from devtools_testutils.aio import recorded_by_proxy_async
from sb_env_loader import ServiceBusPreparer


class TestServiceBusManagementClientNamespaceAsync(AzureMgmtRecordedTestCase):
    @ServiceBusPreparer()
    @recorded_by_proxy_async
    async def test_async_mgmt_namespace_get_properties(
        self, servicebus_connection_str, servicebus_fully_qualified_namespace, servicebus_sas_policy, servicebus_sas_key
    ):
        credential = get_credential(is_async=True)
        mgmt_service = ServiceBusAdministrationClient(
            fully_qualified_namespace=servicebus_fully_qualified_namespace, credential=credential
        )
        properties = await mgmt_service.get_namespace_properties()
        assert properties
        assert properties.messaging_sku == "Standard"
        # assert properties.name == servicebus_fully_qualified_namespace.name
        # This is disabled pending investigation of why it isn't getting scrubbed despite expected scrubber use.
