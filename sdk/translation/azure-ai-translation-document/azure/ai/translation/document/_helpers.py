# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import datetime
from typing import Union
import six
from azure.core.pipeline.policies import HttpLoggingPolicy


def get_http_logging_policy(**kwargs):
    http_logging_policy = HttpLoggingPolicy(**kwargs)
    http_logging_policy.allowed_header_names.update(
        {
            "Operation-Location",
            "Content-Encoding",
            "Vary",
            "apim-request-id",
            "X-RequestId",
            "Set-Cookie",
            "X-Powered-By",
            "Strict-Transport-Security",
            "x-content-type-options"
        }
    )
    http_logging_policy.allowed_query_params.update(
        {
            "$top",
            "$skip",
            "$maxpagesize",
            "ids",
            "statuses",
            "createdDateTimeUtcStart",
            "createdDateTimeUtcEnd",
            "$orderBy"
        }
    )
    return http_logging_policy


def convert_datetime(date_time):
    # type: (Union[str, datetime.datetime]) -> datetime.datetime
    if isinstance(date_time, datetime.datetime):
        return date_time
    if isinstance(date_time, six.string_types):
        try:
            return datetime.datetime.strptime(date_time, "%Y-%m-%d")
        except ValueError:
            try:
                return datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                return datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    raise TypeError("Bad datetime type")