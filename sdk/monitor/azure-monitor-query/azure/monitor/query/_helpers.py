#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from json import loads

from azure.core.exceptions import HttpResponseError

from ._utils.serialization import Serializer, Deserializer


def order_results(request_order: List, mapping: Dict[str, Any], **kwargs: Any) -> List:
    ordered = [mapping[id] for id in request_order]
    results = []
    for item in ordered:
        # In rare cases, the generated value is a JSON string instead of a dict. This potentially stems from a bug in
        # the service. This check handles that case.
        if isinstance(item["body"], str):
            item["body"] = loads(item["body"])
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
