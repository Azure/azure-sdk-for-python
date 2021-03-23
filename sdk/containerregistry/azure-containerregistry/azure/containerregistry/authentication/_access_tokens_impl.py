# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


class AccessTokensImpl(object):
    """Provides access to all the operations defined in AcessTokensService"""

    def __init__(self, url, pipeline, client):
        # type: (str, HttpPipeline, ContainerRegistry) -> None
        self.url = url
        self.service = pipeline

    def get_access_token_with_response(self, grant_type, service_name, scope, refresh_token):
        # type: (str, str, str, str) -> AcrAccessToken
        return self.service.get_access_token(self.url, grant_type, service_name, scope, refresh_token)

    def get_access_token(self, grant_type, service_name, scope, refresh_token):
        # type: (str, str, str, str) -> AccessToken
        return self.get_access_token_with_response(grant_type, service_name, scope, refresh_token)

    def get_access_token(self, url, grant_type, service, scope, refresh_token):
        # type: (str, str, str, str, str) -> AcrAccessToken
        _models_access_token = self._client.access_tokens.get(service, scope, refresh_token)
        return AcrAccessToken._from_generated(_models_access_token)
