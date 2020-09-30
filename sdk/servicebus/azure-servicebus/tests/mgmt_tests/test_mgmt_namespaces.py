#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest

from azure.servicebus.management import ServiceBusAdministrationClient

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import CachedServiceBusNamespacePreparer


class ServiceBusManagementClientNamespaceTests(AzureMgmtTestCase):
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_mgmt_namespace_get_properties(self, servicebus_namespace_connection_string,
                                           servicebus_namespace, servicebus_namespace_key_name,
                                           servicebus_namespace_primary_key):
        mgmt_service = ServiceBusAdministrationClient.from_connection_string(servicebus_namespace_connection_string)
        properties = mgmt_service.get_namespace_properties()
        assert properties
        assert properties.messaging_sku == 'Standard'
        # assert properties.name == servicebus_namespace.name
        # This is disabled pending investigation of why it isn't getting scrubbed despite expected scrubber use.