# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.credentials import AccessToken


def test_accesstoken_compatibility():
    """AccessToken should remain compatible with its original namedtuple implementation"""

    access_token = "***"
    expires_on = 42000

    def assert_namedtuple_api_compatibility(token):
        # AccessToken should have the same API as a namedtuple with "token" and "expires_on" fields
        assert token == (access_token, expires_on)
        assert token.token == access_token
        assert token.expires_on == expires_on
        assert token._asdict() == {"token": access_token, "expires_on": expires_on}

    # should be able to construct AccessToken with only "token" and "expires_on"
    for token in (AccessToken(access_token, expires_on), AccessToken(token=access_token, expires_on=expires_on)):
        assert_namedtuple_api_compatibility(token)

        # refresh_on defaults to expires_on - 300
        assert token.refresh_on == expires_on - 300

    # refresh_on is an optional positional parameter AccessToken doesn't return during unpacking or iteration
    refresh_on = 42
    for token in (
        AccessToken(access_token, expires_on, refresh_on),
        AccessToken(access_token, expires_on, refresh_on=refresh_on),
    ):
        assert_namedtuple_api_compatibility(token)
        assert token.refresh_on == refresh_on
