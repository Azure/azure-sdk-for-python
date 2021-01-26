# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.credentials import AccessToken

from ._jwt import _retrieve_jwt_expiration_timestamp
from .._generated.models import StsTokenResponseMessage

def _convert_to_access_token(token_response_message):
    # type: (StsTokenResponseMessage) -> AccessToken
    """
    Converts the specified token response message to an AccessToken.
    """
    if not StsTokenResponseMessage:
        raise ValueError("token_response_message can not be None")

    expiration_timestamp = _retrieve_jwt_expiration_timestamp(token_response_message.access_token)

    return AccessToken(token_response_message.access_token, expiration_timestamp)
