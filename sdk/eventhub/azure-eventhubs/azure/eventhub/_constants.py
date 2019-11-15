# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

from uamqp import types  # type: ignore


PROP_SEQ_NUMBER = b"x-opt-sequence-number"
PROP_OFFSET = b"x-opt-offset"
PROP_PARTITION_KEY = b"x-opt-partition-key"
PROP_PARTITION_KEY_AMQP_SYMBOL = types.AMQPSymbol(PROP_PARTITION_KEY)
PROP_TIMESTAMP = b"x-opt-enqueued-time"
PROP_LAST_ENQUEUED_SEQUENCE_NUMBER = b"last_enqueued_sequence_number"
PROP_LAST_ENQUEUED_OFFSET = b"last_enqueued_offset"
PROP_LAST_ENQUEUED_TIME_UTC = b"last_enqueued_time_utc"
PROP_RUNTIME_INFO_RETRIEVAL_TIME_UTC = b"runtime_info_retrieval_time_utc"

EPOCH_SYMBOL = b'com.microsoft:epoch'
TIMEOUT_SYMBOL = b'com.microsoft:timeout'
RECEIVER_RUNTIME_METRIC_SYMBOL = b'com.microsoft:enable-receiver-runtime-metric'

ALL_PARTITIONS = "all-partitions"
CONTAINER_PREFIX = "eventhub.pysdk-"
JWT_TOKEN_SCOPE = "https://eventhubs.azure.net//.default"
MGMT_OPERATION = b'com.microsoft:eventhub'
MGMT_PARTITION_OPERATION = b'com.microsoft:partition'

NO_RETRY_ERRORS = (
    b"com.microsoft:argument-out-of-range",
    b"com.microsoft:entity-disabled",
    b"com.microsoft:auth-failed",
    b"com.microsoft:precondition-failed",
    b"com.microsoft:argument-error"
)