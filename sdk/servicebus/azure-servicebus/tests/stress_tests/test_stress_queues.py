#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from datetime import datetime, timedelta
import logging
import pytest
import sys
import time

from azure.servicebus import ServiceBusClient
from azure.servicebus._common.constants import ReceiveSettleMode

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer

from servicebus_preparer import ServiceBusNamespacePreparer, ServiceBusQueuePreparer
from stress_tests.stress_test_base import StressTestRunner, ReceiveType
from utilities import get_logger

_logger = get_logger(logging.DEBUG)

class ServiceBusQueueStressTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_send_and_receive(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, debug=False)

        stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       duration=timedelta(seconds=60))

        result = stress_test.Run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_send_and_pull_receive(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, debug=False)

        stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       receive_type=ReceiveType.pull,
                                       duration=timedelta(seconds=60))

        result = stress_test.Run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_batch_send_and_receive(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, debug=False)

        stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       duration=timedelta(seconds=60),
                                       send_batch_size=5)

        result = stress_test.Run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_slow_send_and_receive(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, debug=False)

        stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       duration=timedelta(seconds=3501*3),
                                       send_delay=3500)

        result = stress_test.Run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_receive_and_delete(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, debug=False)

        stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name, mode=ReceiveSettleMode.ReceiveAndDelete)],
                                       duration=timedelta(seconds=60))

        result = stress_test.Run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)