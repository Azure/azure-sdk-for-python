#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING
from msrest import Serializer
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

def order_results(request_order, responses):
    mapping = {item.id: item for item in responses}
    ordered = [mapping[id] for id in request_order]
    return ordered

def construct_iso8601(start=None, end=None, duration=None):
    iso_str = None
    if start is not None:
        start = Serializer.serialize_iso(start)
        if end is not None:
            end = Serializer.serialize_iso(end)
            iso_str = start + '/' + end
        elif duration is not None:
            iso_str = start + '/' + duration
        else:
            raise ValueError("Start time must be provided aling with duration or end time.")
    elif end is not None:
        end = Serializer.serialize_iso(end)
        iso_str = duration + '/' + end
    else:
        iso_str = duration
    return iso_str
