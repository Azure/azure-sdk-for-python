# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# pylint: disable=protected-access

"""Regression tests for pyAMQP session window accounting (azure-sdk-for-python#49232)."""

from unittest.mock import MagicMock

import pytest

from azure.servicebus._pyamqp._encode import encode_uint, encode_ulong
from azure.servicebus._pyamqp.constants import SessionState
from azure.servicebus._pyamqp.session import Session


def _session(*, incoming_window=4, outgoing_window=4):
    connection = MagicMock(name="connection")
    connection._remote_max_frame_size = 4096
    session = Session(
        connection,
        channel=0,
        incoming_window=incoming_window,
        outgoing_window=outgoing_window,
        network_trace=False,
        network_trace_params={},
    )
    session.state = SessionState.MAPPED
    return session, connection


def test_outgoing_transfer_does_not_exhaust_local_outgoing_window():
    session, connection = _session(outgoing_window=1)
    session.remote_incoming_window = 1

    delivery = MagicMock(name="delivery")
    delivery.frame = {
        "payload": b"x",
        "handle": 0,
        "delivery_tag": b"tag",
        "message_format": 0,
        "settled": False,
        "rcv_settle_mode": None,
        "state": None,
        "resume": False,
        "aborted": False,
        "batchable": False,
    }

    session._outgoing_transfer(delivery, network_trace_params=None)

    assert session.outgoing_window == 1
    assert session.remote_incoming_window == 0
    assert session.next_outgoing_id == 1
    assert connection._process_outgoing_frame.call_count == 1


def test_incoming_window_recovers_after_transfer_handler_exception():
    session, connection = _session(incoming_window=1)
    session.next_incoming_id = 0
    session.remote_outgoing_window = 2

    link = MagicMock(name="link")
    link._incoming_transfer.side_effect = [RuntimeError("handler failed"), None]
    session._input_handles[0] = link

    with pytest.raises(RuntimeError, match="handler failed"):
        session._incoming_transfer((0,))

    assert session.incoming_window == 0

    session._incoming_transfer((0,))

    assert session.incoming_window == session.target_incoming_window == 1
    assert connection._process_outgoing_frame.call_count == 1


@pytest.mark.parametrize("encoder", [encode_uint, encode_ulong])
@pytest.mark.parametrize("value", [-1, -255, -256])
def test_unsigned_encoders_reject_negative_values(encoder, value):
    with pytest.raises(ValueError, match="invalid"):
        encoder(bytearray(), value)
