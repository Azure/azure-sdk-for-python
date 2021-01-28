# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import base64
import json

def _retrieve_jwt_expiration_timestamp(jwt_value):
    # type: (str) -> int
    """
    Retrieves the expiration value from the JWT.

    :param str jwt_value: The JWT value.
    :returns: int
    """
    if not jwt_value:
        raise ValueError("jwt_value can not be None")

    parts = jwt_value.split(".")

    if len(parts) < 3:
        raise ValueError("Invalid JWT structure.")

    try:
        padded_base64_payload = base64.b64decode(parts[1])
        payload = json.loads(padded_base64_payload)
    except ValueError:
        raise ValueError("Unable to decode the JWT.")

    try:
        exp = payload['exp']
    except KeyError:
        raise ValueError("Invalid JWT payload structure. No expiration.")

    return int(exp)
