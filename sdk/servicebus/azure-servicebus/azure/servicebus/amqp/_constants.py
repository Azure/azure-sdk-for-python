# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from enum import Enum

from uamqp import MessageBodyType


class AMQPMessageBodyType(str, Enum):
    DATA = "data"
    SEQUENCE = "sequence"
    VALUE = "value"


AMQP_MESSAGE_BODY_TYPE_MAP = {
    MessageBodyType.Data.value: AMQPMessageBodyType.DATA,
    MessageBodyType.Sequence.value: AMQPMessageBodyType.SEQUENCE,
    MessageBodyType.Value.value: AMQPMessageBodyType.VALUE,
}