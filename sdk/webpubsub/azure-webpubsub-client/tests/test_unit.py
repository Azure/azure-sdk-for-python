# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import json
from azure.webpubsub.client import WebPubSubJsonReliableProtocol
from azure.webpubsub.client._models import JoinGroupMessage, JoinGroupData
from testcase import WebpubsubClientTest, WebpubsubClientPowerShellPreparer

def compare_dict(dict1, dict2):
    assert json.dumps(dict1, sort_keys=True) == json.dumps(dict2, sort_keys=True)

@pytest.mark.parametrize(
    "testname, message, expect",
    [
        ("JoinGroup1", JoinGroupMessage(group="group"), {"type": "joinGroup", "group": "group"}),
    ],
)
def test_write_message(testname, message, expect):
    protocol = WebPubSubJsonReliableProtocol()
    message = protocol.write_message(message)
    compare_dict(json.loads(message), expect)
