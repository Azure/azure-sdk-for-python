#------------------------------------------------------------------------- 
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from datetime import timedelta
import time
import os
from dotenv import load_dotenv
from argparse import ArgumentParser

from azure.servicebus import AutoLockRenewer, ServiceBusClient, TransportType
from azure.servicebus.management import ServiceBusAdministrationClient
from azure.servicebus._common.constants import ServiceBusReceiveMode
from app_insights_metric import AzureMonitorMetric

from stress_test_base import StressTestRunner, ReceiveType

ENV_FILE = os.environ.get('ENV_FILE')


def test_stress_queue_send_and_receive(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME)],
                                    admin_client = sb_admin_client,
                                    duration=args.duration,
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_send_and_receive")
                                    )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")

def test_stress_queue_send_and_pull_receive(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME)],
                                    admin_client = sb_admin_client,
                                    receive_type=ReceiveType.pull,
                                    duration=args.duration,
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_send_and_pull_receive")
                                    )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")

def test_stress_queue_batch_send_and_receive(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME, prefetch_count=5)],
                                    admin_client = sb_admin_client,
                                    duration=args.duration,
                                    send_batch_size=5,
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_batch_send_and_receive")
                                    )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")

def test_stress_queue_batch_send_and_receive_u(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    uamqp_sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE, uamqp_transport=True)
    stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [uamqp_sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME, prefetch_count=5)],
                                    admin_client = sb_admin_client,
                                    duration=args.duration,
                                    send_batch_size=5,
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_batch_send_and_receive")
                                    )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")

def test_stress_queue_slow_send_and_receive(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME)],
                                    admin_client = sb_admin_client,
                                    # duration=timedelta(seconds=3501*3),
                                    duration=args.duration,
                                    send_delay=(args.duration/3),
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_slow_send_and_receive")
                                    )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")

def test_stress_queue_receive_and_delete(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE)],
                                    admin_client = sb_admin_client,
                                    should_complete_messages = False,
                                    duration=args.duration,
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_slow_send_and_receive")
                                    )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")

def test_stress_queue_unsettled_messages(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME)],
                                    admin_client = sb_admin_client,
                                    # duration = timedelta(seconds=350),
                                    duration=args.duration,
                                    should_complete_messages = False,
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_unsettled_messages")
                                    )

    result = stress_test.run()
    # This test is prompted by reports of an issue where enough unsettled messages saturate a service-side cache
    # and prevent further receipt.
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")

def test_stress_queue_receive_large_batch_size(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    stress_test = StressTestRunner(senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME, prefetch_count=50)],
                                    admin_client = sb_admin_client,
                                    duration = args.duration,
                                    max_message_count = 50,
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_receive_large_batch_size")
                                    )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")

# Cannot be defined at local scope due to pickling into multiproc runner.
class ReceiverTimeoutStressTestRunner(StressTestRunner):
    def on_send(self, state, sent_message, sender):
        '''Called on every successful send'''
        if state.total_sent % 10 == 0:
            # To make receive time out, in push mode this delay would trigger receiver reconnection
            time.sleep(self.max_wait_time + 5)

def test_stress_queue_pull_receive_timeout(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    stress_test = ReceiverTimeoutStressTestRunner(
        senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
        receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME)],
        admin_client = sb_admin_client,
        max_wait_time = 5,
        receive_type=ReceiveType.pull,
        # duration=timedelta(seconds=600),
        duration=args.duration,
        azure_monitor_metric=AzureMonitorMetric("test_stress_queue_pull_receive_timeout")
        )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")

class LongRenewStressTestRunner(StressTestRunner):
    def on_receive(self, state, received_message, receiver):
        '''Called on every successful receive'''
        renewer = AutoLockRenewer()
        renewer.register(receiver, received_message, max_lock_renewal_duration=300)
        time.sleep(300)

def test_stress_queue_long_renew_send_and_receive(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    stress_test = LongRenewStressTestRunner(
                                    senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME)],
                                    admin_client = sb_admin_client,
                                    # duration=timedelta(seconds=3000),
                                    duration=args.duration,
                                    send_delay=300,
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_long_renew_send_and_receive")
                                    )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")

class LongSessionRenewStressTestRunner(StressTestRunner):
    def on_receive(self, state, received_message, receiver):
        '''Called on every successful receive'''
        renewer = AutoLockRenewer()
        def on_fail(renewable, error):
            print("FAILED AUTOLOCKRENEW: " + str(error))
        renewer.register(receiver, receiver.session, max_lock_renewal_duration=600, on_lock_renew_failure=on_fail)

def test_stress_queue_long_renew_session_send_and_receive(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    session_id = 'test_stress_queue_long_renew_send_and_receive'

    stress_test = LongSessionRenewStressTestRunner(
                                    senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME, session_id=session_id)],
                                    admin_client = sb_admin_client,
                                    # duration=timedelta(seconds=3000),
                                    duration=args.duration,
                                    send_delay=300,
                                    send_session_id=session_id,
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_long_renew_session_send_and_receive")
                                    )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")


class Peekon_receiveStressTestRunner(StressTestRunner):
    def on_receive_batch(self, state, received_message, receiver):
        '''Called on every successful receive'''
        assert receiver.peek_messages()[0]

def test_stress_queue_peek_messages(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    stress_test = Peekon_receiveStressTestRunner(
                                    senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME)],
                                    admin_client = sb_admin_client,
                                    # duration = timedelta(seconds=300),
                                    duration=args.duration,
                                    receive_delay = 30,
                                    receive_type = ReceiveType.none,
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_peek_messages")
                                    )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")
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

def test_stress_queue_close_and_reopen(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    stress_test = RestartHandlerStressTestRunner(
                                    senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME)],
                                    admin_client = sb_admin_client,
                                    # duration = timedelta(seconds=300),
                                    duration = args.duration,
                                    receive_delay = 30,
                                    send_delay = 10,
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_close_and_reopen")
                                    )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")

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
            _message_id = 0
            body = 0
        _message_id += 1

        return str(body)

def test_stress_queue_check_for_dropped_messages(args):
    sb_client = ServiceBusClient.from_connection_string(
        SERVICE_BUS_CONNECTION_STR, logging_enable=LOGGING_ENABLE, transport_type=TRANSPORT_TYPE)
    stress_test = DroppedMessageCheckerStressTestRunner(
                                    senders = [sb_client.get_queue_sender(SERVICEBUS_QUEUE_NAME)],
                                    receivers = [sb_client.get_queue_receiver(SERVICEBUS_QUEUE_NAME)],
                                    admin_client = sb_admin_client,
                                    receive_type=ReceiveType.pull,
                                    # duration=timedelta(seconds=3000),
                                    duration=args.duration,
                                    azure_monitor_metric=AzureMonitorMetric("test_stress_queue_check_for_dropped_messages")
                                    )

    result = stress_test.run()
    print(f"Total send {result.total_sent}")
    print(f"Total received {result.total_received}")

if __name__ == '__main__':
    load_dotenv(dotenv_path=ENV_FILE, override=True)
    parser = ArgumentParser()
    parser.add_argument("--conn_str", help="ServiceBus connection string",
        default=os.environ.get('SERVICE_BUS_CONNECTION_STR'))
    parser.add_argument("--queue_name", help="The queue name.", default="testQueue")
    parser.add_argument("--method", type=str)
    parser.add_argument("--duration", type=int, default=259200)
    parser.add_argument("--logging-enable", action="store_true")
    parser.add_argument("--print_console", action="store_true")

    parser.add_argument("--send-batch-size", type=int, default=100)
    parser.add_argument("--message-size", type=int, default=100)

    parser.add_argument("--receive-type", type=str, default="pull")
    parser.add_argument("--max_wait_time", type=int, default=10)
    parser.add_argument("--max_message_count", type=int, default=1)
    parser.add_argument("--uamqp_mode", action="store_true")
    parser.add_argument("--transport", action="store_true")

    args, _ = parser.parse_known_args()

    if args.transport:
        TRANSPORT_TYPE= TransportType.AmqpOverWebsocket
    else:
        TRANSPORT_TYPE= TransportType.Amqp

    SERVICE_BUS_CONNECTION_STR = args.conn_str
    SERVICEBUS_QUEUE_NAME= args.queue_name
    LOGGING_ENABLE = args.logging_enable

    sb_admin_client = ServiceBusAdministrationClient.from_connection_string(SERVICE_BUS_CONNECTION_STR)

    if args.method == "send_receive":
        test_stress_queue_send_and_receive(args)    
    elif args.method == "send_pull_receive":
        test_stress_queue_send_and_pull_receive(args)
    elif args.method == "send_receive_batch":
        test_stress_queue_batch_send_and_receive(args)
    elif args.method == "uamqp":
        test_stress_queue_batch_send_and_receive_u(args)
    elif args.method == "send_receive_slow":
        test_stress_queue_slow_send_and_receive(args)
    elif args.method == "receive_delete":
        test_stress_queue_receive_and_delete(args)
    elif args.method == "unsettled_message":
        test_stress_queue_unsettled_messages(args)
    elif args.method == "large_batch":
        test_stress_queue_receive_large_batch_size(args)
    elif args.method == "pull_receive_timeout":
        test_stress_queue_pull_receive_timeout(args)
    elif args.method == "long_renew":
        test_stress_queue_long_renew_send_and_receive(args)
    elif args.method == "long_renew_session":
        test_stress_queue_long_renew_session_send_and_receive(args)
    elif args.method == "queue_peek":
        test_stress_queue_peek_messages(args)
    elif args.method == "queue_close_reopen":
        test_stress_queue_close_and_reopen(args)
    elif args.method == "dropped_messages":
        test_stress_queue_check_for_dropped_messages(args)
    else:
        test_stress_queue_send_and_receive(args)    
        test_stress_queue_send_and_pull_receive(args)
        test_stress_queue_batch_send_and_receive(args)
        test_stress_queue_slow_send_and_receive(args)
        test_stress_queue_receive_and_delete(args)
        test_stress_queue_unsettled_messages(args)
        test_stress_queue_receive_large_batch_size(args)
        test_stress_queue_pull_receive_timeout(args)
        test_stress_queue_long_renew_send_and_receive(args)
        test_stress_queue_long_renew_session_send_and_receive(args)
        test_stress_queue_peek_messages(args)
        test_stress_queue_close_and_reopen(args)
        test_stress_queue_check_for_dropped_messages(args)

