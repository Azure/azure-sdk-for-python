# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime
import isodate

def verify_datetime_format(input_datetime):
    #type: (datetime) -> bool
    if input_datetime is None:
        return True
    try:
        if isinstance(input_datetime, str):
            input_datetime = isodate.parse_datetime(input_datetime)
        if isinstance(input_datetime, datetime):
            return True
    except:
        raise ValueError("{} is not a valid ISO-8601 datetime format".format(input_datetime)) from None
    return True
    