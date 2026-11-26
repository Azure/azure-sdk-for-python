# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# pylint: disable=protected-access

import threading
from unittest.mock import Mock, call

import pytest

from azure.servicebus import AutoLockRenewer, ServiceBusReceivedMessage, ServiceBusReceiveMode, ServiceBusReceiver
from azure.servicebus._common.utils import utc_now


def _receiver(renewer, uamqp_transport, configuration="message"):
    if uamqp_transport:
        pytest.importorskip("uamqp")
    receive_mode = (
        ServiceBusReceiveMode.RECEIVE_AND_DELETE
        if configuration in ("receive-delete", "session-receive-delete")
        else ServiceBusReceiveMode.PEEK_LOCK
    )
    receiver = ServiceBusReceiver(
        "test.servicebus.windows.net",
        Mock(),
        queue_name="queue",
        auto_lock_renewer=None if configuration in ("disabled", "receive-delete") else renewer,
        receive_mode=receive_mode,
        session_id="session" if configuration in ("session", "session-receive-delete") else None,
        uamqp_transport=uamqp_transport,
        retry_total=0,
    )
    receiver._open = Mock()
    receiver._handler = Mock()
    receiver._running = True
    return receiver


def _messages(receiver, count):
    messages = []
    for _ in range(count):
        message = Mock(spec=ServiceBusReceivedMessage)
        message._receiver = receiver
        message._received_timestamp_utc = utc_now()
        message.locked_until_utc = utc_now()
        message._lock_expired = False
        message._settled = False
        message.application_properties = {}
        messages.append(message)
    receiver._receive = Mock(return_value=messages)
    receiver._mgmt_request_response_with_retry = Mock(return_value=messages)
    raw_messages = [object() for _ in messages]
    receiver._handler.receive_messages_iter.return_value = iter(raw_messages)
    receiver._build_received_message = Mock(side_effect=messages)
    return messages


def _receive(receiver, entry, count):
    if entry == "batch":
        return receiver.receive_messages(max_message_count=count, max_wait_time=1)
    if entry == "deferred":
        return receiver.receive_deferred_messages(list(range(1, count + 1)))
    if entry == "next":
        return [next(receiver) for _ in range(count)]
    assert entry == "iterator"
    return list(receiver)


@pytest.mark.parametrize("uamqp_transport", [False, True], ids=["pyamqp", "uamqp"])
@pytest.mark.parametrize("entry", ["batch", "deferred", "next", "iterator"])
@pytest.mark.parametrize(
    "configuration", ["message", "session", "session-receive-delete", "receive-delete", "disabled"]
)
def test_receive_entry_points_register_each_message_only_when_eligible(entry, configuration, uamqp_transport):
    renewer = Mock(spec=AutoLockRenewer)
    receiver = _receiver(renewer, uamqp_transport, configuration)
    messages = _messages(receiver, 2)
    try:
        assert _receive(receiver, entry, len(messages)) == messages
        if configuration == "message":
            assert renewer.register.call_args_list == [call(receiver, message) for message in messages]
        else:
            renewer.register.assert_not_called()
        assert not receiver._receive_context.is_set()
    finally:
        receiver.close()


@pytest.mark.parametrize("uamqp_transport", [False, True], ids=["pyamqp", "uamqp"])
@pytest.mark.parametrize("entry", ["batch", "deferred", "next", "iterator"])
def test_automatic_registration_reaches_real_renewal_worker(entry, uamqp_transport):
    if uamqp_transport:
        pytest.importorskip("uamqp")
    renewer = AutoLockRenewer(max_workers=2)
    renewer._sleep_time = 0.01
    receiver = _receiver(renewer, uamqp_transport)
    messages = _messages(receiver, 2)
    completed = threading.Event()
    callback = Mock()
    renewer._on_lock_renew_failure = callback

    def renew(message):
        message._settled = True
        if all(message._settled for message in messages):
            completed.set()

    receiver.renew_message_lock = Mock(side_effect=renew)
    try:
        assert _receive(receiver, entry, len(messages)) == messages
        assert completed.wait(timeout=5)
        with renewer._renew_tasks.all_tasks_done:
            assert renewer._renew_tasks.all_tasks_done.wait_for(
                lambda: renewer._renew_tasks.unfinished_tasks == 0, timeout=5
            )
        assert receiver.renew_message_lock.call_count == len(messages)
        assert {id(invocation.args[0]) for invocation in receiver.renew_message_lock.call_args_list} == {
            id(message) for message in messages
        }
        callback.assert_not_called()
        assert renewer._renew_tasks.empty()
    finally:
        renewer.close()
        receiver.close()


@pytest.mark.parametrize("uamqp_transport", [False, True], ids=["pyamqp", "uamqp"])
def test_receive_and_delete_rejects_automatic_message_lock_renewal(uamqp_transport):
    if uamqp_transport:
        pytest.importorskip("uamqp")
    with pytest.raises(ValueError, match="RECEIVE_AND_DELETE"):
        ServiceBusReceiver(
            "test.servicebus.windows.net",
            Mock(),
            queue_name="queue",
            receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
            auto_lock_renewer=Mock(spec=AutoLockRenewer),
            uamqp_transport=uamqp_transport,
        )
