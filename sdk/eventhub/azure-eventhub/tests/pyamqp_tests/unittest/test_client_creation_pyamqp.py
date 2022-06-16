# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest

from azure.eventhub._pyamqp import SendClient, ReceiveClient

def test_send_client_creation():

    sender = SendClient(
        "fake.host.com",
        "fake_eh",
        "my_fake_auth"
    )
    assert sender.target == "fake_eh"
    assert sender._auth == "my_fake_auth"


def test_receive_client_creation():

    receiver = ReceiveClient(
        "fake.host.com",
        "fake_eh",
        "my_fake_auth"
    )
    assert receiver.source == "fake_eh"
    assert receiver._auth == "my_fake_auth"
