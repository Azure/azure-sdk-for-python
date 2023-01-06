# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import timedelta

def convert_timedelta_to_mins(
    duration, # type: timedelta
):
    # type: (...) -> int
    """
    Returns the total number of minutes contained in the duration.
    : param duration: Time duration
    : type duration: ~datetime.timedelta
    : rtype: int
    """
    return None if duration is None else int(duration.total_seconds() / 60)
