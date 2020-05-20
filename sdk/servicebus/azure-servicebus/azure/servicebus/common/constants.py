# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from enum import Enum

from uamqp import constants

VENDOR = b"com.microsoft"
DATETIMEOFFSET_EPOCH = 621355968000000000

ENQUEUEDTIMEUTCNAME = b"x-opt-enqueued-time"
SCHEDULEDENQUEUETIMENAME = b"x-opt-scheduled-enqueue-time"
SEQUENCENUBMERNAME = b"x-opt-sequence-number"
LOCKTOKENNAME = b"x-opt-lock-token"
LOCKEDUNTILNAME = b"x-opt-locked-until"
PARTITIONKEYNAME = b"x-opt-partition-key"
DEADLETTERSOURCENAME = b"x-opt-deadletter-source"
DEADLETTERNAME = VENDOR + b":dead-letter"
ASSOCIATEDLINKPROPERTYNAME = b"associated-link-name"

SESSION_FILTER = VENDOR + b":session-filter"
SESSION_LOCKED_UNTIL = VENDOR + b":locked-until-utc"
SESSION_LOCK_LOST = VENDOR + b":session-lock-lost"
SESSION_LOCK_TIMEOUT = VENDOR + b":timeout"

REQUEST_RESPONSE_OPERATION_NAME = b"operation"
REQUEST_RESPONSE_TIMEOUT = VENDOR + b":server-timeout"
REQUEST_RESPONSE_RENEWLOCK_OPERATION = VENDOR + b":renew-lock"
REQUEST_RESPONSE_RENEW_SESSION_LOCK_OPERATION = VENDOR + b":renew-session-lock"
REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER = VENDOR + b":receive-by-sequence-number"
REQUEST_RESPONSE_SCHEDULE_MESSAGE_OPERATION = VENDOR + b":schedule-message"
REQUEST_RESPONSE_CANCEL_SCHEDULED_MESSAGE_OPERATION = VENDOR + b":cancel-scheduled-message"
REQUEST_RESPONSE_PEEK_OPERATION = VENDOR + b":peek-message"
REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION = VENDOR + b":update-disposition"
REQUEST_RESPONSE_GET_SESSION_STATE_OPERATION = VENDOR + b":get-session-state"
REQUEST_RESPONSE_SET_SESSION_STATE_OPERATION = VENDOR + b":set-session-state"
REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION = VENDOR + b":get-message-sessions"
REQUEST_RESPONSE_ADD_RULE_OPERATION = VENDOR + b":add-rule"
REQUEST_RESPONSE_REMOVE_RULE_OPERATION = VENDOR + b":remove-rule"
REQUEST_RESPONSE_GET_RULES_OPERATION = VENDOR + b":enumerate-rules"

RECEIVER_LINK_DEAD_LETTER_REASON = 'DeadLetterReason'
RECEIVER_LINK_DEAD_LETTER_DESCRIPTION = 'DeadLetterErrorDescription'

class ReceiveSettleMode(Enum):
    PeekLock = constants.ReceiverSettleMode.PeekLock
    ReceiveAndDelete = constants.ReceiverSettleMode.ReceiveAndDelete


class SessionFilter(Enum):
    NextAvailable = 0


NEXT_AVAILABLE = SessionFilter.NextAvailable
