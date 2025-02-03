# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime, timedelta, timezone
from dateutil import parser
from azure.communication.identity import CommunicationTokenScope


def is_token_expiration_within_allowed_deviation(expected_token_expiration, token_expires_in, allowed_deviation=0.05):
    # type: (timedelta, datetime, float) -> bool
    utc_now = datetime.now(timezone.utc)
    token_expiration = parser.parse(str(token_expires_in))
    token_expiration_in_seconds = (token_expiration - utc_now).total_seconds()
    expected_seconds = expected_token_expiration.total_seconds()
    time_difference = abs(expected_seconds - token_expiration_in_seconds)
    allowed_time_difference = expected_seconds * allowed_deviation
    return time_difference < allowed_time_difference


token_scope_scenarios = [
    ("ChatScope", [CommunicationTokenScope.CHAT]),
    ("VoipScope", [CommunicationTokenScope.VOIP]),
    ("ChatJoinScope", [CommunicationTokenScope.CHAT_JOIN]),
    ("ChatJoinLimitedScope", [CommunicationTokenScope.CHAT_JOIN_LIMITED]),
    ("VoipJoinScope", [CommunicationTokenScope.VOIP_JOIN]),
    ("ChatVoipScopes", [CommunicationTokenScope.VOIP, CommunicationTokenScope.CHAT]),
    (
        "AllChatScopes",
        [
            CommunicationTokenScope.CHAT,
            CommunicationTokenScope.CHAT_JOIN,
            CommunicationTokenScope.CHAT_JOIN_LIMITED,
        ],
    ),
    (
        "AllVoipScopes",
        [CommunicationTokenScope.VOIP, CommunicationTokenScope.VOIP_JOIN],
    ),
    (
        "ChatJoinVoipJoinScopes",
        [CommunicationTokenScope.CHAT_JOIN, CommunicationTokenScope.VOIP_JOIN],
    ),
]
