# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import base64
import json
import random

from azure.core.credentials import AccessToken

from ._generated.models import StsTokenResponseMessage


def convert_to_access_token(token_response_message):
    # type: (StsTokenResponseMessage) -> AccessToken
    """
    Converts the specified token response message to an AccessToken.
    """
    if not token_response_message:
        raise ValueError("token_response_message must be a non-empty string.")

    expiration_timestamp = retrieve_jwt_expiration_timestamp(token_response_message.access_token)

    return AccessToken(token_response_message.access_token, expiration_timestamp)

def retrieve_jwt_expiration_timestamp(jwt_value):
    # type: (str) -> int
    """
    Retrieves the expiration value from the JWT.

    :param str jwt_value: The JWT value.
    :returns: int
    """
    if not jwt_value:
        raise ValueError("jwt_value must be a non-empty string.")

    parts = jwt_value.split(".")

    if len(parts) < 3:
        raise ValueError("Invalid JWT structure. Expected a JWS Compact Serialization formatted value.")

    try:
        # JWT prefers no padding (see https://tools.ietf.org/id/draft-jones-json-web-token-02.html#base64urlnotes).
        # We pad the value with the max padding of === to keep our logic simple and allow the base64 decoder to handle
        # the value properly. b64decode will properly trim the padding appropriately, but apparently doesn't want to
        # handle the addition of padding.
        padded_base64_payload = base64.b64decode(parts[1] + "===").decode('utf-8')
        payload = json.loads(padded_base64_payload)
    except ValueError:
        raise ValueError("Unable to decode the JWT.")

    try:
        exp = payload['exp']
    except KeyError:
        raise ValueError("Invalid JWT payload structure. No expiration.")

    return int(exp)

BASE_64_CHAR_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
CV_BASE_LENGTH = 22

def generate_cv_base():
    # type: () -> str
    """
    Seed function to randomly generate a 16 character base64 encoded string for
    the Correlation Vector's base value.
    """
    result = ''

    #pylint: disable=unused-variable
    for i in range(CV_BASE_LENGTH):
        random_index = random.randint(0, len(BASE_64_CHAR_SET) - 1)
        result += BASE_64_CHAR_SET[random_index]

    return result
