#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
from unittest.mock import Mock
from base64 import encode
import os
import sys
import pytest
import uuid

root_path = os.path.realpath('.')
sys.path.append(root_path)

from azure.eventhub._pyamqp.types import AMQPTypes
from azure.eventhub._pyamqp.utils import amqp_uint_value, amqp_long_value, amqp_string_value

def test_uint_value():
    value = amqp_uint_value(255)
    assert value.get("VALUE") == 255
    assert value.get("TYPE") == AMQPTypes.uint


def test_long_value():
    value = amqp_long_value(255)
    assert value.get("VALUE") == 255
    assert value.get("TYPE") == AMQPTypes.long

def test_string_value():
    value = amqp_string_value("hello")
    assert value.get("VALUE") == "hello"
    assert value.get("TYPE") == AMQPTypes.string