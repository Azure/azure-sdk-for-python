# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime, timedelta, timezone
from dateutil import parser
from msal import PublicClientApplication

def is_token_expiration_within_allowed_deviation(
    expected_token_expiration,
    token_expires_in,
    allowed_deviation = 0.05
):
    # type: (timedelta, datetime, float) -> bool
    utc_now = datetime.now(timezone.utc)
    token_expiration = parser.parse(token_expires_in)
    token_expiration_in_seconds = (token_expiration - utc_now).total_seconds()
    expected_seconds = expected_token_expiration.total_seconds();
    time_difference = abs(expected_seconds - token_expiration_in_seconds)
    allowed_time_difference = expected_seconds * allowed_deviation
    return time_difference < allowed_time_difference

def generate_teams_user_aad_token(self):
    if self.is_playback():
        teams_user_aad_token = "sanitized"
        teams_user_oid = "sanitized"
    else:
        msal_app = PublicClientApplication(
            client_id=self.m365_client_id,
            authority="{}/{}".format(self.m365_aad_authority, self.m365_aad_tenant))
        scopes = [
            "https://auth.msft.communication.azure.com/Teams.ManageCalls",
            "https://auth.msft.communication.azure.com/Teams.ManageChats"
        ]
        result = msal_app.acquire_token_by_username_password(username=self.msal_username, password=self.msal_password, scopes=scopes)
        teams_user_aad_token = result["access_token"]
        teams_user_oid = result["id_token_claims"]["oid"]
    return teams_user_aad_token, teams_user_oid

def skip_get_token_for_teams_user_test(skip_get_token):
    return str(skip_get_token).lower() == 'true'
