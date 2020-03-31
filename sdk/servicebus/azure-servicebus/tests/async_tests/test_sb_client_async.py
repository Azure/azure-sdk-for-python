#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest

from azure.servicebus.aio import (
    ServiceBusClient)
from uamqp.constants import TransportType
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer
from servicebus_preparer import (
    ServiceBusNamespacePreparer
)

class ServiceBusClientAsyncTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @RandomNameResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    def test_servicebusclient_from_conn_str_amqpoverwebsocket_async(self, servicebus_namespace_connection_string, **kwargs):
        sb_client = ServiceBusClient.from_connection_string(servicebus_namespace_connection_string)
        assert sb_client.transport_type == TransportType.Amqp

        websocket_sb_client = ServiceBusClient.from_connection_string(servicebus_namespace_connection_string + ';TransportType=AmqpOverWebsocket')
        assert websocket_sb_client.transport_type == TransportType.AmqpOverWebsocket
