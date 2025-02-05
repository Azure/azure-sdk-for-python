# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from enum import Enum


PROP_SEQ_NUMBER = b"x-opt-sequence-number"
PROP_OFFSET = b"x-opt-offset"
PROP_PARTITION_KEY = b"x-opt-partition-key"
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
GEOREPLICATION_SYMBOL = b"com.microsoft:georeplication"

MAX_MESSAGE_LENGTH_BYTES = 1024 * 1024
MAX_USER_AGENT_LENGTH = 512
ALL_PARTITIONS = "all-partitions"
CONTAINER_PREFIX = "eventhub.pysdk-"
JWT_TOKEN_SCOPE = "https://eventhubs.azure.net//.default"
MGMT_OPERATION = b"com.microsoft:eventhub"
MGMT_PARTITION_OPERATION = b"com.microsoft:partition"
MGMT_STATUS_CODE = b"status-code"
MGMT_STATUS_DESC = b"status-description"
USER_AGENT_PREFIX = "azsdk-python-eventhubs"
UAMQP_LIBRARY = "uamqp"
PYAMQP_LIBRARY = "pyamqp"
MAX_BUFFER_LENGTH = 300

NO_RETRY_ERRORS = [
    b"com.microsoft:argument-out-of-range",
    b"com.microsoft:entity-disabled",
    b"com.microsoft:auth-failed",
    b"com.microsoft:precondition-failed",
    b"com.microsoft:argument-error",
]

CUSTOM_CONDITION_BACKOFF = {
    b"com.microsoft:server-busy": 4,
    b"com.microsoft:timeout": 2,
    b"com.microsoft:operation-cancelled": 0,
    b"com.microsoft:container-close": 4,
}


## all below - previously uamqp
class TransportType(Enum):
    """Transport type
    The underlying transport protocol type:
    Amqp: AMQP over the default TCP transport protocol, it uses port 5671.
    AmqpOverWebsocket: Amqp over the Web Sockets transport protocol, it uses
    port 443.
    """

    Amqp = 1
    AmqpOverWebsocket = 2


DEFAULT_AMQPS_PORT = 5671
DEFAULT_AMQP_WSS_PORT = 443
READ_OPERATION = b"READ"
