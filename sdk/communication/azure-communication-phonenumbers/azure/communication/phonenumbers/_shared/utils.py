# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import base64
import json
import calendar
from typing import cast, Tuple, Optional
from datetime import datetime
from msrest.serialization import TZ_UTC
from azure.core.credentials import AccessToken


def _convert_datetime_to_utc_int(input_datetime) -> int:
    """
    Converts DateTime in local time to the Epoch in UTC in second.

    :param input_datetime: Input datetime
    :type input_datetime: datetime
    :return: Integer
    :rtype: int
    """
    return int(calendar.timegm(input_datetime.utctimetuple()))


def parse_connection_str(conn_str):
    # type: (Optional[str]) -> Tuple[str, str]
    if conn_str is None:
        raise ValueError("Connection string is undefined.")
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
        host = cast(str, endpoint)[left_slash_pos + 2 :]
    else:
        host = str(endpoint)

    return host, str(shared_access_key)


def get_current_utc_time():
    # type: () -> str
    return str(datetime.now(tz=TZ_UTC).strftime("%a, %d %b %Y %H:%M:%S ")) + "GMT"


def get_current_utc_as_int():
    # type: () -> int
    current_utc_datetime = datetime.utcnow()
    return _convert_datetime_to_utc_int(current_utc_datetime)


def create_access_token(token):
    # type: (str) -> AccessToken
    """Creates an instance of azure.core.credentials.AccessToken from a
    string token. The input string is jwt token in the following form:
    <token_header>.<token_payload>.<token_signature>
    This method looks into the token_payload which is a json and extracts the expiry time
    for that token and creates a tuple of type azure.core.credentials.AccessToken
    (<string_token>, <expiry>)
    :param token: User token
    :type token: str
    :return: Instance of azure.core.credentials.AccessToken - token and expiry date of it
    :rtype: ~azure.core.credentials.AccessToken
    """

    token_parse_err_msg = "Token is not formatted correctly"
    parts = token.split(".")

    if len(parts) < 3:
        raise ValueError(token_parse_err_msg)

    try:
        padded_base64_payload = base64.b64decode(parts[1] + "==").decode("ascii")
        payload = json.loads(padded_base64_payload)
        return AccessToken(
            token,
            _convert_datetime_to_utc_int(
                datetime.fromtimestamp(payload["exp"], TZ_UTC)
            ),
        )
    except ValueError as val_error:
        raise ValueError(token_parse_err_msg) from val_error
