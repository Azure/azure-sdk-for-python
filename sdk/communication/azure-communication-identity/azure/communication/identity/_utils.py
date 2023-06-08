# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import timedelta, datetime
from uuid import uuid1


def convert_timedelta_to_mins(
        duration,  # type: timedelta
):
    # type: (...) -> int
    """
    Returns the total number of minutes contained in the duration.
    : param duration: Time duration
    : type duration: ~datetime.timedelta
    : rtype: int
    """
    return None if duration is None else int(duration.total_seconds() / 60)


def get_repeatability_headers():
    """ Initializes and returns Repeatability Headers """
    repeatability_request_id = uuid1()
    repeatability_first_sent = datetime.utcnow()
    return repeatability_request_id, repeatability_first_sent
