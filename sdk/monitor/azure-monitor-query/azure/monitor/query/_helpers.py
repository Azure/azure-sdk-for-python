#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from msrest import Serializer, Deserializer
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import BearerTokenCredentialPolicy

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

def get_authentication_policy(
        credential, # type: TokenCredential
):
    # type: (...) -> BearerTokenCredentialPolicy
    """Returns the correct authentication policy
    """

    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        return BearerTokenCredentialPolicy(credential, "https://api.loganalytics.io/.default")

    raise TypeError("Unsupported credential")

def get_metrics_authentication_policy(
        credential, # type: TokenCredential
):
    # type: (...) -> BearerTokenCredentialPolicy
    """Returns the correct authentication policy
    """

    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        return BearerTokenCredentialPolicy(credential, "https://management.azure.com/.default")

    raise TypeError("Unsupported credential")

def process_error(exception):
    raise_error = HttpResponseError
    raise raise_error(message=exception.message, response=exception.response)

def order_results(request_order, mapping, obj):
    ordered = [mapping[id] for id in request_order]
    return [obj._from_generated(rsp) for rsp in ordered] # pylint: disable=protected-access

def construct_iso8601(timespan=None):
    if not timespan:
        return None
    try:
        start, end, duration = None, None, None
        if isinstance(timespan[1], datetime): # we treat thi as start_time, end_time
            start, end = timespan[0], timespan[1]
        elif isinstance(timespan[1], timedelta): # we treat this as start_time, duration
            start, duration = timespan[0], timespan[1]
        else:
            raise ValueError('Tuple must be a start datetime with a timedelta or an end datetime.')
    except TypeError:
        duration = timespan # it means only duration (timedelta) is provideds
    if duration:
        try:
            duration = 'PT{}S'.format(duration.total_seconds())
        except AttributeError:
            raise ValueError('timespan must be a timedelta or a tuple.')
    iso_str = None
    if start is not None:
        start = Serializer.serialize_iso(start)
        if end is not None:
            end = Serializer.serialize_iso(end)
            iso_str = start + '/' + end
        elif duration is not None:
            iso_str = start + '/' + duration
        else: # means that an invalid value None that is provided with start_time
            raise ValueError("Duration or end_time cannot be None when provided with start_time.")
    else:
        iso_str = duration
    return iso_str

def native_col_type(col_type, value):
    if col_type == 'datetime':
        value = Deserializer.deserialize_iso(value)
    elif col_type in ('timespan', 'guid'):
        value = str(value)
    return value

def process_row(col_types, row):
    return [native_col_type(col_types[ind], val) for ind, val in enumerate(row)]
