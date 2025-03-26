# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from azure.servicebus.management import ServiceBusAdministrationClient

from devtools_testutils import AzureMgmtRecordedTestCase, CachedResourceGroupPreparer, recorded_by_proxy, get_credential
from sb_env_loader import ServiceBusPreparer


class TestServiceBusManagementClientNamespace(AzureMgmtRecordedTestCase):
    @ServiceBusPreparer()
    @recorded_by_proxy
    def test_mgmt_namespace_get_properties(
        self, servicebus_connection_str, servicebus_fully_qualified_namespace, servicebus_sas_policy, servicebus_sas_key
    ):
        credential = get_credential()
        mgmt_service = ServiceBusAdministrationClient(
            fully_qualified_namespace=servicebus_fully_qualified_namespace, credential=credential
        )
        properties = mgmt_service.get_namespace_properties()
        assert properties
        assert properties.messaging_sku == "Standard"
        # assert properties.name == servicebus_fully_qualified_namespace.name
        # This is disabled pending investigation of why it isn't getting scrubbed despite expected scrubber use.
