#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple, Union

from azure.core.credentials import TokenCredential
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import BearerTokenCredentialPolicy

from ._generated._serialization import Serializer, Deserializer


def get_authentication_policy(credential: TokenCredential, audience: str) -> BearerTokenCredentialPolicy:
    """Returns the correct authentication policy.

    :param credential: The credential to use for authentication with the service.
    :type credential: ~azure.core.credentials.TokenCredential
    :param str audience: The audience for the token.
    :returns: The correct authentication policy.
    :rtype: ~azure.core.pipeline.policies.BearerTokenCredentialPolicy
    """
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    scope = audience.rstrip("/") + "/.default"
    if hasattr(credential, "get_token"):
        return BearerTokenCredentialPolicy(credential, scope)

    raise TypeError("Unsupported credential")


def order_results(request_order: List, mapping: Dict[str, Any], **kwargs: Any) -> List:
    ordered = [mapping[id] for id in request_order]
    results = []
    for item in ordered:
        if not item["body"].get("error"):
            result_obj = kwargs.get("obj")
            if result_obj:
                results.append(result_obj._from_generated(item["body"]))  # pylint: disable=protected-access
        else:
            error = item["body"]["error"]
            if error.get("code") == "PartialError":
                partial_err = kwargs.get("partial_err")
                if partial_err:
                    res = partial_err._from_generated(  # pylint: disable=protected-access
                        item["body"], kwargs.get("raise_with")
                    )
                    results.append(res)
            else:
                err = kwargs.get("err")
                if err:
                    results.append(err._from_generated(error))  # pylint: disable=protected-access
    return results


def construct_iso8601(timespan=None) -> Optional[str]:
    if not timespan:
        return None
    start, end, duration = None, None, None
    try:
        if isinstance(timespan[1], datetime):  # we treat thi as start_time, end_time
            start, end = timespan[0], timespan[1]
        elif isinstance(timespan[1], timedelta):  # we treat this as start_time, duration
            start, duration = timespan[0], timespan[1]
        else:
            raise ValueError("Tuple must be a start datetime with a timedelta or an end datetime.")
    except TypeError:
        duration = timespan  # it means only duration (timedelta) is provideds
    duration_str = ""
    if duration:
        try:
            duration_str = "PT{}S".format(duration.total_seconds())
        except AttributeError as e:
            raise ValueError("timespan must be a timedelta or a tuple.") from e
    iso_str = None
    if start is not None:
        start = Serializer.serialize_iso(start)
        if end is not None:
            end = Serializer.serialize_iso(end)
            iso_str = f"{start}/{end}"
        elif duration_str:
            iso_str = f"{start}/{duration_str}"
        else:  # means that an invalid value None that is provided with start_time
            raise ValueError("Duration or end_time cannot be None when provided with start_time.")
    else:
        iso_str = duration_str
    return iso_str


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


def native_col_type(col_type, value):
    if col_type == "datetime":
        try:
            value = Deserializer.deserialize_iso(value)
        except Exception:  # pylint: disable=broad-except
            # if there is any exception in deserializing the iso,
            # return the value to the user
            pass
    elif col_type in ("timespan", "guid"):
        value = str(value)
    return value


def process_row(col_types, row) -> List[Any]:
    return [native_col_type(col_types[ind], val) for ind, val in enumerate(row)]


def process_error(error, model):
    try:
        model = model._from_generated(error.model.error)  # pylint: disable=protected-access
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
