# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

from uamqp import types


PROP_SEQ_NUMBER = b"x-opt-sequence-number"
PROP_OFFSET = b"x-opt-offset"
PROP_PARTITION_KEY = b"x-opt-partition-key"
PROP_PARTITION_KEY_AMQP_SYMBOL = types.AMQPSymbol(PROP_PARTITION_KEY)
PROP_TIMESTAMP = b"x-opt-enqueued-time"
PROP_LAST_ENQUEUED_SEQUENCE_NUMBER = b"last_enqueued_sequence_number"
PROP_LAST_ENQUEUED_OFFSET = b"last_enqueued_offset"
PROP_LAST_ENQUEUED_TIME_UTC = b"last_enqueued_time_utc"
PROP_RUNTIME_INFO_RETRIEVAL_TIME_UTC = b"runtime_info_retrieval_time_utc"

PROP_MESSAGE_ID = b"message-id"
PROP_USER_ID = b"user-id"
PROP_TO = b"to"
PROP_SUBJECT = b"subject"
PROP_REPLY_TO = b"reply-to"
PROP_CORRELATION_ID = b"correlation-id"
PROP_CONTENT_TYPE = b"content-type"
PROP_CONTENT_ENCODING = b"content-encoding"
PROP_ABSOLUTE_EXPIRY_TIME = b"absolute-expiry-time"
PROP_CREATION_TIME = b"creation-time"
PROP_GROUP_ID = b"group-id"
PROP_GROUP_SEQUENCE = b"group-sequence"
PROP_REPLY_TO_GROUP_ID = b"reply-to-group-id"

EPOCH_SYMBOL = b"com.microsoft:epoch"
TIMEOUT_SYMBOL = b"com.microsoft:timeout"
RECEIVER_RUNTIME_METRIC_SYMBOL = b"com.microsoft:enable-receiver-runtime-metric"

MAX_USER_AGENT_LENGTH = 512
ALL_PARTITIONS = "all-partitions"
CONTAINER_PREFIX = "eventhub.pysdk-"
JWT_TOKEN_SCOPE = "https://eventhubs.azure.net//.default"
MGMT_OPERATION = b"com.microsoft:eventhub"
MGMT_PARTITION_OPERATION = b"com.microsoft:partition"
MGMT_STATUS_CODE = b"status-code"
MGMT_STATUS_DESC = b"status-description"
USER_AGENT_PREFIX = "azsdk-python-eventhubs"

NO_RETRY_ERRORS = (
    b"com.microsoft:argument-out-of-range",
    b"com.microsoft:entity-disabled",
    b"com.microsoft:auth-failed",
    b"com.microsoft:precondition-failed",
    b"com.microsoft:argument-error",
)
