# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from uamqp import BatchMessage, constants, MessageBodyType
from ...amqp._constants import AmqpMessageBodyType

AMQP_MESSAGE_BODY_TYPE_MAP = {
    MessageBodyType.Data.value: AmqpMessageBodyType.DATA,
    MessageBodyType.Sequence.value: AmqpMessageBodyType.SEQUENCE,
    MessageBodyType.Value.value: AmqpMessageBodyType.VALUE,
}

BATCH_MESSAGE = BatchMessage
MAX_MESSAGE_LENGTH_BYTES = constants.MAX_MESSAGE_LENGTH_BYTES
