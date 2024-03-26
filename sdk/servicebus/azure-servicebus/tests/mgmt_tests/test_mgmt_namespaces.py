#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest

from azure.servicebus.management import ServiceBusAdministrationClient

from devtools_testutils import AzureMgmtRecordedTestCase, CachedResourceGroupPreparer, recorded_by_proxy
from tests.sb_env_loader import ServiceBusPreparer


class TestServiceBusManagementClientNamespace(AzureMgmtRecordedTestCase):
    @ServiceBusPreparer()
    @recorded_by_proxy
    def test_mgmt_namespace_get_properties(self, servicebus_connection_str,
                                           servicebus_fully_qualified_namespace, servicebus_sas_policy,
                                           servicebus_sas_key):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_connection_str)
        properties = mgmt_service.get_namespace_properties()
        assert properties
        assert properties.messaging_sku == 'Standard'
        # assert properties.name == servicebus_fully_qualified_namespace.name
        # This is disabled pending investigation of why it isn't getting scrubbed despite expected scrubber use.