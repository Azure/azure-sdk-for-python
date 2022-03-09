#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Dict, Any
from msrest import Serializer, Deserializer
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import BearerTokenCredentialPolicy

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


def get_authentication_policy(
    credential,  # type: "TokenCredential"
    audience=None # type: str
):
    # type: (...) -> BearerTokenCredentialPolicy
    """Returns the correct authentication policy"""
    if not audience:
        audience = "https://api.loganalytics.io/"
    scope = audience.rstrip('/') + "/.default"
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        return BearerTokenCredentialPolicy(
            credential, scope
        )

    raise TypeError("Unsupported credential")


def get_metrics_authentication_policy(
    credential,  # type: TokenCredential
    audience=None # type: str
):
    # type: (...) -> BearerTokenCredentialPolicy
    """Returns the correct authentication policy"""
    if not audience:
        audience = "https://management.azure.com/"
    scope = audience.rstrip('/') + "/.default"
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        return BearerTokenCredentialPolicy(
            credential, scope
        )

    raise TypeError("Unsupported credential")


def order_results(request_order, mapping, **kwargs):
    # type: (List, Dict, Any) -> List
    ordered = [mapping[id] for id in request_order]
    results = []
    for item in ordered:
        if not item.body.error:
            results.append(
                kwargs.get("obj")._from_generated(item.body) # pylint: disable=protected-access
            )
        else:
            error = item.body.error
            if error.code == "PartialError":
                res = kwargs.get("partial_err")._from_generated(  # pylint: disable=protected-access
                    item.body, kwargs.get("raise_with")
                )
                results.append(res)
            else:
                results.append(
                    kwargs.get("err")._from_generated(error) # pylint: disable=protected-access
                )
    return results


def construct_iso8601(timespan=None):
    if not timespan:
        return None
    try:
        start, end, duration = None, None, None
        if isinstance(timespan[1], datetime):  # we treat thi as start_time, end_time
            start, end = timespan[0], timespan[1]
        elif isinstance(
            timespan[1], timedelta
        ):  # we treat this as start_time, duration
            start, duration = timespan[0], timespan[1]
        else:
            raise ValueError(
                "Tuple must be a start datetime with a timedelta or an end datetime."
            )
    except TypeError:
        duration = timespan  # it means only duration (timedelta) is provideds
    if duration:
        try:
            duration = "PT{}S".format(duration.total_seconds())
        except AttributeError:
            raise ValueError("timespan must be a timedelta or a tuple.")
    iso_str = None
    if start is not None:
        start = Serializer.serialize_iso(start)
        if end is not None:
            end = Serializer.serialize_iso(end)
            iso_str = start + "/" + end
        elif duration is not None:
            iso_str = start + "/" + duration
        else:  # means that an invalid value None that is provided with start_time
            raise ValueError(
                "Duration or end_time cannot be None when provided with start_time."
            )
    else:
        iso_str = duration
    return iso_str


def native_col_type(col_type, value):
    if col_type == "datetime":
        try:
            value = Deserializer.deserialize_iso(value)
        except Exception: # pylint: disable=broad-except
            # if there is any exception in deserializing the iso,
            # return the value to the user
            pass
    elif col_type in ("timespan", "guid"):
        value = str(value)
    return value


def process_row(col_types, row):
    return [native_col_type(col_types[ind], val) for ind, val in enumerate(row)]


def process_error(error, model):
    try:
        model = model._from_generated( # pylint: disable=protected-access
            error.model.error
        )
    except AttributeError:  # model can be none
        pass
    raise HttpResponseError(message=error.message, response=error.response, model=model)


def process_prefer(server_timeout, include_statistics, include_visualization):
    prefer = ""
    if server_timeout:
        prefer += "wait=" + str(server_timeout) + ","
    if include_statistics:
        prefer += "include-statistics=true,"
    if include_visualization:
        prefer += "include-render=true"
    return prefer.rstrip(",")
