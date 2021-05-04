#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
import threading
from datetime import datetime, timedelta
import concurrent
import sys
import uuid
import logging

try:
    import psutil
except ImportError:
    pass # If psutil isn't installed, simply does not capture process stats.

from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusMessageBatch
from azure.servicebus.exceptions import MessageAlreadySettled

from utilities import _build_logger
_logger = _build_logger("stress-test", logging.WARN)

class ReceiveType:
    push="push"
    pull="pull"
    none=None


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
        self.cpu_percent = None
        self.memory_bytes = None
        self.timestamp = None
        self.exceptions = []

    def __repr__(self):
        return str(vars(self))

    def populate_process_stats(self):
        self.timestamp = datetime.utcnow()
        try:
            self.cpu_percent = psutil.cpu_percent()
            self.memory_bytes = psutil.virtual_memory().total
        except NameError:
            return # psutil was not installed, fall back to simply not capturing these stats.

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
                 max_message_count = 1,
                 send_session_id = None,
                 fail_on_exception = True):
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
        self.fail_on_exception = fail_on_exception
        self.send_session_id = send_session_id

        # Because of pickle we need to create a state object and not just pass around ourselves.
        # If we ever require multiple runs of this one after another, just make Run() reset this.
        self._state = StressTestRunnerState()

        self._duration_override = None
        for arg in sys.argv:
            if arg.startswith('--stress_test_duration_seconds='):
                self._duration_override = timedelta(seconds=int(arg.split('=')[1]))

        self._should_stop = False


    # Plugin functions the caller can override to further tailor the test.
    def on_send(self, state, sent_message, sender):
        '''Called on every successful send, per message'''
        pass

    def on_receive(self, state, received_message, receiver):
        '''Called on every successful receive, per message'''
        pass

    def on_receive_batch(self, state, batch, receiver):
        '''Called on every successful receive, at the batch or iterator level rather than per-message'''
        pass

    def post_receive(self, state, receiver):
        '''Called after completion of every successful receive'''
        pass

    def on_complete(self, send_results=[], receive_results=[]):
        '''Called on stress test run completion'''
        pass


    def pre_process_message(self, message):
        '''Allows user to transform the message before batching or sending it.'''
        pass


    def pre_process_message_batch(self, message):
        '''Allows user to transform the batch before sending it.'''
        pass


    def pre_process_message_body(self, payload):
        '''Allows user to transform message payload before sending it.'''
        return payload


    def _schedule_interval_logger(self, end_time, description="", interval_seconds=30):
        def _do_interval_logging():
            if end_time > datetime.utcnow() and not self._should_stop:
                self._state.populate_process_stats()
                _logger.critical("{} RECURRENT STATUS: {}".format(description, self._state))
                self._schedule_interval_logger(end_time, description, interval_seconds)

        t = threading.Timer(interval_seconds, _do_interval_logging)
        t.start()


    def _construct_message(self):
        if self.send_batch_size != None:
            batch = ServiceBusMessageBatch()
            for _ in range(self.send_batch_size):
                message = ServiceBusMessage(self.pre_process_message_body("a" * self.message_size))
                self.pre_process_message(message)
                batch.add_message(message)
            self.PreProcessMessageBatch(batch)
            return batch
        else:
            message = ServiceBusMessage(self.pre_process_message_body("a" * self.message_size))
            self.pre_process_message(message)
            return message


    def _send(self, sender, end_time):
        self._schedule_interval_logger(end_time, "Sender " + str(self))
        try:
            _logger.info("STARTING SENDER")
            with sender:
                while end_time > datetime.utcnow() and not self._should_stop:
                    _logger.info("SENDING")
                    try:
                        message = self._construct_message()
                        if self.send_session_id != None:
                            message.session_id = self.send_session_id
                        sender.send_messages(message)
                        self.on_send(self._state, message, sender)
                    except Exception as e:
                        _logger.exception("Exception during send: {}".format(e))
                        self._state.exceptions.append(e)
                        if self.fail_on_exception:
                            raise
                    self._state.total_sent += 1
                    time.sleep(self.send_delay)
            self._state.timestamp = datetime.utcnow()
            return self._state
        except Exception as e:
            _logger.exception("Exception in sender: {}".format(e))
            self._should_stop = True
            raise

    def _receive(self, receiver, end_time):
        self._schedule_interval_logger(end_time, "Receiver " + str(self))
        try:
            with receiver:
                while end_time > datetime.utcnow() and not self._should_stop:
                    _logger.info("RECEIVE LOOP")
                    try:
                        if self.receive_type == ReceiveType.pull:
                            batch = receiver.receive_messages(max_message_count=self.max_message_count, max_wait_time=self.max_wait_time)
                        elif self.receive_type == ReceiveType.push:
                            batch = receiver._get_streaming_message_iter(max_wait_time=self.max_wait_time)
                        else:
                            batch = []

                        for message in batch:
                            self.on_receive(self._state, message, receiver)
                            try:
                                if self.should_complete_messages:
                                    receiver.complete_message(message)
                            except MessageAlreadySettled: # It may have been settled in the plugin callback.
                                pass
                            self._state.total_received += 1
                            #TODO: Get EnqueuedTimeUtc out of broker properties and calculate latency. Should properties/app properties be mostly None?
                            if end_time <= datetime.utcnow():
                                break
                            time.sleep(self.receive_delay)
                        self.post_receive(self._state, receiver)
                    except Exception as e:
                        _logger.exception("Exception during receive: {}".format(e))
                        self._state.exceptions.append(e)
                        if self.fail_on_exception:
                            raise
            self._state.timestamp = datetime.utcnow()
            return self._state
        except Exception as e:
            _logger.exception("Exception in receiver {}".format(e))
            self._should_stop = True
            raise


    def run(self):
        start_time = datetime.utcnow()
        end_time = start_time + (self._duration_override or self.duration)
        sent_messages = 0
        received_messages = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as proc_pool:
            _logger.info("STARTING PROC POOL")
            senders = [proc_pool.submit(self._send, sender, end_time) for sender in self.senders]
            receivers = [proc_pool.submit(self._receive, receiver, end_time) for receiver in self.receivers]

            result = StressTestResults()
            for each in concurrent.futures.as_completed(senders + receivers):
                _logger.info("SOMETHING FINISHED")
                if each in senders:
                    result.state_by_sender[each] = each.result()
                if each in receivers:
                    result.state_by_receiver[each] = each.result()
            # TODO: do as_completed in one batch to provide a way to short-circuit on failure.
            result.state_by_sender = {s:f.result() for s,f in zip(self.senders, concurrent.futures.as_completed(senders))}
            result.state_by_receiver = {r:f.result() for r,f in zip(self.receivers, concurrent.futures.as_completed(receivers))}
            _logger.info("got receiever results")
            result.total_sent = sum([r.total_sent for r in result.state_by_sender.values()])
            result.total_received = sum([r.total_received for r in result.state_by_receiver.values()])
            result.time_elapsed = end_time - start_time
            _logger.critical("Stress test completed.  Results:\n{}".format(result))
            return result

