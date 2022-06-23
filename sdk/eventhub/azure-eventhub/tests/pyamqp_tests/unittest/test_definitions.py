#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import sys
import pytest

from azure.eventhub._pyamqp.message import Header, Message
from azure.eventhub._pyamqp._encode import encode_annotations
from azure.eventhub._pyamqp.utils import AMQPTypes


def test_header():
    value = Header()
    assert value is not None


def test_annotations():
    test_value = {"TYPE": AMQPTypes.int, "VALUE": 10}
    value = encode_annotations(test_value)

    assert value is not test_value

