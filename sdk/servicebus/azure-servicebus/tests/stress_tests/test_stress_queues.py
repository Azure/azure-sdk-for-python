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

from azure.servicebus import ServiceBusClient, AutoLockRenewer
from azure.servicebus._common.constants import ServiceBusReceiveMode

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer

from servicebus_preparer import ServiceBusNamespacePreparer, ServiceBusQueuePreparer
from stress_tests.stress_test_base import StressTestRunner, ReceiveType

LOGGING_ENABLE = False

class ServiceBusQueueStressTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_send_and_receive(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=LOGGING_ENABLE)

        stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       duration=timedelta(seconds=60))

        result = stress_test.run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_send_and_pull_receive(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=LOGGING_ENABLE)

        stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       receive_type=ReceiveType.pull,
                                       duration=timedelta(seconds=60))

        result = stress_test.run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_batch_send_and_receive(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=LOGGING_ENABLE)

        stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       duration=timedelta(seconds=60),
                                       send_batch_size=5)

        result = stress_test.run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_slow_send_and_receive(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=LOGGING_ENABLE)

        stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       duration=timedelta(seconds=3501*3),
                                       send_delay=3500)

        result = stress_test.run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_receive_and_delete(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=LOGGING_ENABLE)

        stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE)],
                                       should_complete_messages = False,
                                       duration=timedelta(seconds=60))

        result = stress_test.run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_unsettled_messages(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=LOGGING_ENABLE)

        stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       duration = timedelta(seconds=350),
                                       should_complete_messages = False)

        result = stress_test.run()
        # This test is prompted by reports of an issue where enough unsettled messages saturate a service-side cache
        # and prevent further receipt.
        assert(result.total_sent > 2500)
        assert(result.total_received > 2500)


    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_receive_large_batch_size(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=LOGGING_ENABLE)

        stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name, prefetch_count=50)],
                                       duration = timedelta(seconds=60),
                                       max_message_count = 50)

        result = stress_test.run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)

    # Cannot be defined at local scope due to pickling into multiproc runner.
    class ReceiverTimeoutStressTestRunner(StressTestRunner):
        def on_send(self, state, sent_message, sender):
            '''Called on every successful send'''
            if state.total_sent % 10 == 0:
                # To make receive time out, in push mode this delay would trigger receiver reconnection
                time.sleep(self.max_wait_time + 5)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_pull_receive_timeout(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, logging_enable=LOGGING_ENABLE)
        
        stress_test = ServiceBusQueueStressTests.ReceiverTimeoutStressTestRunner(
            senders = [sb_client.get_queue_sender(servicebus_queue.name)],
            receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
            max_wait_time = 5,
            receive_type=ReceiveType.pull,
            duration=timedelta(seconds=600))

        result = stress_test.run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)


    class LongRenewStressTestRunner(StressTestRunner):
        def on_receive(self, state, received_message, receiver):
            '''Called on every successful receive'''
            renewer = AutoLockRenewer()
            renewer.register(receiver, received_message, max_lock_renewal_duration=300)
            time.sleep(300)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_long_renew_send_and_receive(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, debug=False)

        stress_test = ServiceBusQueueStressTests.LongRenewStressTestRunner(
                                       senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       duration=timedelta(seconds=3000),
                                       send_delay=300)

        result = stress_test.run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)


    class LongSessionRenewStressTestRunner(StressTestRunner):
        def on_receive(self, state, received_message, receiver):
            '''Called on every successful receive'''
            renewer = AutoLockRenewer()
            def on_fail(renewable, error):
                print("FAILED AUTOLOCKRENEW: " + str(error))
            renewer.register(receiver, receiver.session, max_lock_renewal_duration=600, on_lock_renew_failure=on_fail)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', requires_session=True)
    def test_stress_queue_long_renew_session_send_and_receive(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, debug=False)

        session_id = 'test_stress_queue_long_renew_send_and_receive'

        stress_test = ServiceBusQueueStressTests.LongSessionRenewStressTestRunner(
                                       senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name, session_id=session_id)],
                                       duration=timedelta(seconds=3000),
                                       send_delay=300,
                                       send_session_id=session_id)

        result = stress_test.run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)


    class Peekon_receiveStressTestRunner(StressTestRunner):
        def on_receive_batch(self, state, received_message, receiver):
            '''Called on every successful receive'''
            assert receiver.peek_messages()[0]

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_peek_messages(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, debug=False)

        stress_test = ServiceBusQueueStressTests.Peekon_receiveStressTestRunner(
                                       senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       duration = timedelta(seconds=300),
                                       receive_delay = 30,
                                       receive_type = ReceiveType.none)

        result = stress_test.run()
        assert(result.total_sent > 0)
        # TODO: This merits better validation, to be implemented alongside full metric spread.


    class RestartHandlerStressTestRunner(StressTestRunner):
        def post_receive(self, state, receiver):
            '''Called after completion of every successful receive'''
            if state.total_received % 3 == 0:
                receiver.__exit__()
                receiver.__enter__()

        def on_send(self, state, sent_message, sender):
            '''Called after completion of every successful receive'''
            if state.total_sent % 3 == 0:
                sender.__exit__()
                sender.__enter__()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @pytest.mark.skip(reason='This test is disabled unless re-openability of handlers is desired and re-enabled')
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_close_and_reopen(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, debug=False)

        stress_test = ServiceBusQueueStressTests.RestartHandlerStressTestRunner(
                                       senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       duration = timedelta(seconds=300),
                                       receive_delay = 30,
                                       send_delay = 10)

        result = stress_test.run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)

    # This test validates that all individual messages are received contiguously over a long time period.
    # (e.g. not dropped for whatever reason, not sent, or not received)
    class DroppedMessageCheckerStressTestRunner(StressTestRunner):
        def on_receive(self, state, received_message, receiver):
            '''Called on every successful receive'''
            last_seen = getattr(state, 'last_seen', -1)
            noncontiguous = getattr(state, 'noncontiguous', set())
            body = int(str(received_message))
            if body == last_seen+1:
                last_seen += 1
                if noncontiguous:
                    while (last_seen+1) in noncontiguous:
                        last_seen += 1
                        noncontiguous.remove(last_seen)
            else:
                noncontiguous.add(body)
            state.noncontiguous = noncontiguous
            state.last_seen = last_seen

        def pre_process_message_body(self, payload):
            '''Called when constructing message body'''
            try:
                body = self._message_id
            except:
                self._message_id = 0
                body = 0
            self._message_id += 1

            return str(body)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @ServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest')
    def test_stress_queue_check_for_dropped_messages(self, servicebus_namespace_connection_string, servicebus_queue):
        sb_client = ServiceBusClient.from_connection_string(
            servicebus_namespace_connection_string, debug=False)

        stress_test = ServiceBusQueueStressTests.DroppedMessageCheckerStressTestRunner(
                                       senders = [sb_client.get_queue_sender(servicebus_queue.name)],
                                       receivers = [sb_client.get_queue_receiver(servicebus_queue.name)],
                                       receive_type=ReceiveType.pull,
                                       duration=timedelta(seconds=3000))

        result = stress_test.run()
        assert(result.total_sent > 0)
        assert(result.total_received > 0)
