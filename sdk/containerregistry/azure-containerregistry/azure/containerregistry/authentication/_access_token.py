# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

class AccessToken(object):
    """Base access token for ACR challenge based auth flow"""

    def __init__(self, url, pipeline):
        # type: (str, HttpPipeline) -> None
        self.reg_login_url = url

    # Exchange ACR Refresh token for an ACR Access Token
    def get_access_token_with_response(self, grant_type, service_name, scope, refresh_token):
        # type: (str, str, str, str) -> AccessToken
        accept = "application/json"
        return service.get_access_token(
            self.reg_login_url,
            grant_type,
            service_name,
            scope,
            refresh_token,
            accept,
            context
        )

    def get_access_token(self, grant_type, service_name, scope, refresh_token):
        # type: (str, str, str, str) -> AcrAccessToken
        return ""

    