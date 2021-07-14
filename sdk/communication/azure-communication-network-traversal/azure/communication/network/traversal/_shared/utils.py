# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time
from typing import (  # pylint: disable=unused-import
    cast,
    Tuple,
)
from datetime import datetime
import calendar
from msrest.serialization import TZ_UTC

def _convert_datetime_to_utc_int(expires_on):
    return int(calendar.timegm(expires_on.utctimetuple()))

def parse_connection_str(conn_str):
    # type: (str) -> Tuple[str, str, str, str]
    if conn_str is None:
        raise ValueError(
            "Connection string is undefined."
        )
    endpoint = None
    shared_access_key = None
    for element in conn_str.split(";"):
        key, _, value = element.partition("=")
        if key.lower() == "endpoint":
            endpoint = value.rstrip("/")
        elif key.lower() == "accesskey":
            shared_access_key = value
    if not all([endpoint, shared_access_key]):
        raise ValueError(
            "Invalid connection string. You can get the connection string from your resource page in the Azure Portal. "
            "The format should be as follows: endpoint=https://<ResourceUrl>/;accesskey=<KeyValue>"
        )
    left_slash_pos = cast(str, endpoint).find("//")
    if left_slash_pos != -1:
        host = cast(str, endpoint)[left_slash_pos + 2:]
    else:
        host = str(endpoint)

    return host, str(shared_access_key)

def get_current_utc_time():
    # type: () -> str
    return str(datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S ")) + "GMT"

def get_current_utc_as_int():
    # type: () -> int
    current_utc_datetime = datetime.utcnow().replace(tzinfo=TZ_UTC)
    return _convert_datetime_to_utc_int(current_utc_datetime)

def _convert_expires_on_datetime_to_utc_int(expires_on):
    epoch = time.mktime(datetime(1970, 1, 1).timetuple())
    return epoch-time.mktime(expires_on.timetuple())

def get_authentication_policy(
        endpoint, # type: str
        credential, # type: TokenCredential or str
        decode_url=False, # type: bool
        is_async=False, # type: bool
):
    # type: (...) -> BearerTokenCredentialPolicy or HMACCredentialPolicy
    """Returns the correct authentication policy based
    on which credential is being passed.
    :param endpoint: The endpoint to which we are authenticating to.
    :type endpoint: str
    :param credential: The credential we use to authenticate to the service
    :type credential: TokenCredential or str
    :param isAsync: For async clients there is a need to decode the url
    :type bool: isAsync or str
    :rtype: ~azure.core.pipeline.policies.BearerTokenCredentialPolicy
    ~HMACCredentialsPolicy
    """

    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        if is_async:
            from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
            return AsyncBearerTokenCredentialPolicy(
                credential, "https://communication.azure.com//.default")
        from azure.core.pipeline.policies import BearerTokenCredentialPolicy
        return BearerTokenCredentialPolicy(
            credential, "https://communication.azure.com//.default")
    if isinstance(credential, str):
        from .._shared.policy import HMACCredentialsPolicy
        return HMACCredentialsPolicy(endpoint, credential, decode_url=decode_url)

    raise TypeError("Unsupported credential: {}. Use an access token string to use HMACCredentialsPolicy"
                    "or a token credential from azure.identity".format(type(credential)))
