#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
from datetime import datetime, timedelta
import concurrent
import sys
import uuid

from azure.servicebus import ServiceBusClient, Message, BatchMessage
from azure.servicebus._common.constants import ReceiveMode
from azure.servicebus.exceptions import MessageAlreadySettled

class ReceiveType:
    push="push"
    pull="pull"


class StressTestResults(object):
    def __init__(self):
        self.total_sent=0
        self.total_received=0
        self.time_elapsed=None
        self.state_by_sender={}
        self.state_by_receiver={}

    def __repr__(self):
        return str(vars(self))


class StressTestRunnerState(object):
    '''Per-runner state, e.g. if you spawn 3 senders each will have this as their state object,
    which will be coalesced at completion into StressTestResults'''
    def __init__(self):
        self.total_sent=0
        self.total_received=0

    def __repr__(self):
        return str(vars(self))


class StressTestRunner:
    '''Framework for running a service bus stress test.
    Duration can be overriden via the --stress_test_duration flag from the command line'''

    def __init__(self,
                 senders,
                 receivers,
                 duration = timedelta(minutes=15),
                 receive_type = ReceiveType.push,
                 send_batch_size = None,
                 message_size = 10,
                 max_wait_time = 10,
                 send_delay = .01,
                 receive_delay = 0,
                 should_complete_messages = True,
                 max_message_count = 1):
        self.senders = senders
        self.receivers = receivers
        self.duration=duration
        self.receive_type = receive_type
        self.message_size = message_size
        self.send_batch_size = send_batch_size
        self.max_wait_time = max_wait_time
        self.send_delay = send_delay
        self.receive_delay = receive_delay
        self.should_complete_messages = should_complete_messages
        self.max_message_count = max_message_count

        # Because of pickle we need to create a state object and not just pass around ourselves.
        # If we ever require multiple runs of this one after another, just make Run() reset this.
        self._state = StressTestRunnerState()

        self._duration_override = None
        for arg in sys.argv:
            if arg.startswith('--stress_test_duration_seconds='):
                self._duration_override = timedelta(seconds=int(arg.split('=')[1]))


    # Plugin functions the caller can override to further tailor the test.
    def OnSend(self, state, sent_message):
        '''Called on every successful send'''
        pass

    def OnReceive(self, state, received_message):
        '''Called on every successful receive'''
        pass


    def OnComplete(self, send_results=[], receive_results=[]):
        '''Called on stress test run completion'''
        pass


    def PreProcessMessage(self, message):
        '''Allows user to transform the message before batching or sending it.'''
        pass


    def PreProcessMessageBatch(self, message):
        '''Allows user to transform the batch before sending it.'''
        pass


    def PreProcessMessageBody(self, payload):
        '''Allows user to transform message payload before sending it.'''
        return payload


    def _ConstructMessage(self):
        if self.send_batch_size != None:
            batch = BatchMessage()
            for _ in range(self.send_batch_size):
                message = Message(self.PreProcessMessageBody("a" * self.message_size))
                self.PreProcessMessage(message)
                batch.add(message)
            self.PreProcessMessageBatch(batch)
            return batch
        else:
            message = Message(self.PreProcessMessageBody("a" * self.message_size))
            self.PreProcessMessage(message)
            return message


    def _Send(self, sender, end_time):
        try:
            print("STARTING SENDER")
            with sender:
                while end_time > datetime.utcnow():
                    print("SENDING")
                    message = self._ConstructMessage()
                    sender.send_messages(message)
                    self.OnSend(self._state, message)
                    self._state.total_sent += 1
                    time.sleep(self.send_delay)
            return self._state
        except Exception as e:
            print("Exception in sender", e)


    def _Receive(self, receiver, end_time):
        try:
            with receiver:
                while end_time > datetime.utcnow():
                    print("RECEIVE LOOP")
                    if self.receive_type == ReceiveType.pull:
                        batch = receiver.receive_messages(max_message_count=self.max_message_count, max_wait_time=self.max_wait_time)
                    elif self.receive_type == ReceiveType.push:
                        batch = receiver.get_streaming_message_iter(max_wait_time=self.max_wait_time)

                    for message in batch:
                        self.OnReceive(self._state, message)
                        try:
                            if self.should_complete_messages:
                                message.complete()
                        except MessageAlreadySettled: # It may have been settled in the plugin callback.
                            pass
                        self._state.total_received += 1
                        #TODO: Get EnqueuedTimeUtc out of broker properties and calculate latency. Should properties/app properties be mostly None?
                        if end_time <= datetime.utcnow():
                            break
                        time.sleep(self.receive_delay)
            return self._state
        except Exception as e:
            print("Exception in receiver", e)


    def Run(self):
        start_time = datetime.utcnow()
        end_time = start_time + (self._duration_override or self.duration)
        sent_messages = 0
        received_messages = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as proc_pool:
            print("STARTING PROC POOL")
            senders = [proc_pool.submit(self._Send, sender, end_time) for sender in self.senders]
            receivers = [proc_pool.submit(self._Receive, receiver, end_time) for receiver in self.receivers]

            result = StressTestResults()
            for each in concurrent.futures.as_completed(senders + receivers):
                print("SOMETHING FINISHED")
                if each in senders:
                    result.state_by_sender[each] = each.result()
                if each in receivers:
                    result.state_by_receiver[each] = each.result()
            # TODO: do as_completed in one batch to provide a way to short-circuit on failure.
            result.state_by_sender = {s:f.result() for s,f in zip(self.senders, concurrent.futures.as_completed(senders))}
            result.state_by_receiver = {r:f.result() for r,f in zip(self.receivers, concurrent.futures.as_completed(receivers))}
            print("got receiever results")
            result.total_sent = sum([r.total_sent for r in result.state_by_sender.values()])
            result.total_received = sum([r.total_received for r in result.state_by_receiver.values()])
            result.time_elapsed = end_time - start_time
            print("Stress test completed.  Results:\n", result)
            return result

