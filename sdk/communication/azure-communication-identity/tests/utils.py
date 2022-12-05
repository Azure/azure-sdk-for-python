# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime, timedelta, timezone
from dateutil import parser

def is_token_expiration_within_allowed_deviation(
    expected_token_expiration,
    token_expires_in,
    allowed_deviation = 0.05
):
    # type: (timedelta, datetime, float) -> bool
    utc_now = datetime.now(timezone.utc)
    token_expiration = parser.parse(token_expires_in)
    token_expiration_in_seconds = (token_expiration - utc_now).total_seconds()
    expected_seconds = expected_token_expiration.total_seconds();
    time_difference = abs(expected_seconds - token_expiration_in_seconds)
    allowed_time_difference = expected_seconds * allowed_deviation
    return time_difference < allowed_time_difference