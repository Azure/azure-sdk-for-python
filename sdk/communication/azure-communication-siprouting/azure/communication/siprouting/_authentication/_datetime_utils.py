# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import datetime
import calendar

def convert_datetime_to_utc_int(input_datetime):
    # type: (datetime) -> int
    """
    Converts DateTime in local time to the Epoch in UTC in second.

    :param input_datetime: Input datetime
    :type input_datetime: datetime
    :returns: Seconds since epoch.
    :rtype: int
    """
    return int(calendar.timegm(input_datetime.utctimetuple()))


def get_current_utc_as_int():
    # type: () -> int
    """
    Returns current utc datetime as seconds since Epoch.

    :returns: Seconds since epoch.
    :rtype: int
    """
    current_utc_datetime = datetime.utcnow()
    return convert_datetime_to_utc_int(current_utc_datetime)
