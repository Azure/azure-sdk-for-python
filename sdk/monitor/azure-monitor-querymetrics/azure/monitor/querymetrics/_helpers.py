#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Union

from ._utils.serialization import Serializer


def get_timespan_iso8601_endpoints(
    timespan: Optional[Union[timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]]] = None
) -> Tuple[Optional[str], Optional[str]]:

    if not timespan:
        return None, None
    start, end, duration = None, None, None

    if isinstance(timespan, timedelta):
        duration = timespan
    else:
        if isinstance(timespan[1], datetime):
            start, end = timespan[0], timespan[1]
        elif isinstance(timespan[1], timedelta):
            start, duration = timespan[0], timespan[1]
        else:
            raise ValueError("Tuple must be a start datetime with a timedelta or an end datetime.")

    iso_start = None
    iso_end = None
    if start is not None:
        iso_start = Serializer.serialize_iso(start)
        if end is not None:
            iso_end = Serializer.serialize_iso(end)
        elif duration is not None:
            iso_end = Serializer.serialize_iso(start + duration)
        else:  # means that an invalid value None that is provided with start_time
            raise ValueError("Duration or end_time cannot be None when provided with start_time.")
    else:
        # Only duration was provided
        if duration is None:
            raise ValueError("Duration cannot be None when start_time is None.")
        end = datetime.now(timezone.utc)
        iso_end = Serializer.serialize_iso(end)
        iso_start = Serializer.serialize_iso(end - duration)

    # In some cases with a negative timedelta, the start time will be after the end time.
    if iso_start and iso_end and iso_start > iso_end:
        return iso_end, iso_start
    return iso_start, iso_end


def get_subscription_id_from_resource(resource_id: str) -> str:
    """Get the subscription ID from the provided resource ID.

    The format of the resource ID is:
        /subscriptions/{subscriptionId}/resourceGroups/{group}/providers/{provider}/{type}/{name}

    :param str resource_id: The resource ID to parse.
    :returns: The subscription ID.
    :rtype: str
    """
    if not resource_id:
        raise ValueError("Resource ID must not be None or empty.")

    parts = resource_id.split("subscriptions/")
    if len(parts) != 2:
        raise ValueError("Resource ID must contain a subscription ID.")

    subscription_id = parts[1].split("/")[0]
    return subscription_id
