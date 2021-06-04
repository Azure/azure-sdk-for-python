#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Mapping, TYPE_CHECKING
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
