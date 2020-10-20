#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import os

from azure.servicebus import ServiceBusClient, Message


conn_str = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']


def send(sender, end_time):
    with sender:
        while time.time() < end_time:
            sender.send(Message("Message"))
            print('send message')


def schedule(sender, end_time, delay_seconds=30):
    with sender:
        while time.time() < end_time:
            sender.schedule(Message("Scheduled Message"), datetime.utcnow() + timedelta(seconds=delay_seconds))
            print('scheduled message')


def iterator_receive(receiver, end_time):
    with receiver:
        for msg in receiver:
            if time.time() > end_time:
                break
            msg.complete()
            print('complete message in iterator receiver')


def pull_receive(receiver, end_time, max_message_count=None, max_wait_time=None):
    with receiver:
        while time.time() < end_time:
            msgs = receiver.receive()
            for msg in msgs:
                msg.complete()
                print('complete message in pull receiver')


def deferred_letter_receive(receiver, end_time, max_message_count=None, max_wait_time=None):
    with receiver:
        while time.time() < end_time:
            msgs = receiver.receive(max_message_count=max_message_count, max_wait_time=max_wait_time)
            deferred_sequence_numbers = []
            for msg in msgs:
                deferred_sequence_numbers.append(msg.sequence_number)
                msg.defer()
                print('defer a message {}'.format(msg.sequence_number))

            time.sleep(1)

            if deferred_sequence_numbers:
                received_deferred_msgs = receiver.receive_deferred_messages(
                    sequence_numbers=deferred_sequence_numbers
                )

                for deferred_msg in received_deferred_msgs:
                    deferred_msg.complete()
                    print('complete a deferred message')


def dead_letter_receive(receiver, dead_letter_receiver, end_time, max_message_count=None, max_wait_time=None):
    with receiver, dead_letter_receiver:
        while time.time() < end_time:
            msgs = receiver.receive(max_message_count=max_message_count, max_wait_time=max_wait_time)
            for msg in msgs:
                msg.dead_letter("reason", "description")
                print('deadletter a message')

            dl_msgs = dead_letter_receiver.receive(max_message_count=max_message_count, max_wait_time=max_wait_time)
            for msg in dl_msgs:
                msg.complete()
                print('complete a deadletterred message')


if __name__ == '__main__':

    end_time = time.time() + 3600 * 24 * 3

    with ServiceBusClient.from_connection_string(conn_str) as sb_client:
        sender = sb_client.get_queue_sender(queue_name)
        schedule_sender = sb_client.get_queue_sender(queue_name)
        pull_receiver = sb_client.get_queue_receiver(queue_name)
        iterator_receiver = sb_client.get_queue_receiver(queue_name)
        deferred_letter_receiver = sb_client.get_queue_receiver(queue_name)
        dead_letter_help_receiver = sb_client.get_queue_receiver(queue_name)
        dead_letter_queue_receiver = sb_client.get_queue_deadletter_receiver(queue_name)

        with ThreadPoolExecutor(max_workers=6) as executor:
            future_1 = executor.submit(send, sender, end_time)
            future_2 = executor.submit(schedule, schedule_sender, end_time)
            future_3 = executor.submit(iterator_receive, iterator_receiver, end_time)
            future_4 = executor.submit(pull_receive, pull_receiver, end_time)
            future_5 = executor.submit(deferred_letter_receive, deferred_letter_receiver, end_time)
            future_6 = executor.submit(dead_letter_receive, dead_letter_help_receiver, dead_letter_queue_receiver, end_time)

        print(future_1.result())
        print(future_2.result())
        print(future_3.result())
        print(future_4.result())
        print(future_5.result())
        print(future_6.result())
