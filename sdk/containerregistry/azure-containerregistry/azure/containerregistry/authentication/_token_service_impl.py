# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._container_registry_token_request_context import ContainerRegistryTokenRequestContext


class TokenServiceImpl(object):
    """Token service implementation that wraps the authentication REST APIs for ACR"""

    def __init__(self, url, pipeline):
        # type: (str, HttpPipeline) -> None
        self._url = url
        self.pipeline = pipeline
        self.access_token_impl = AccessTokenImpl(url, pipeline)
        self.refresh_token_impl = RefreshTokenImpl(url, pipeline)

    def get_acr_access_token(self, refresh_token, scope, service_name):
        # type: (str, str, str) -> str
        access_token = self.access_token_impl.get_acr_access_token("refresh_token", service_name, scope, refresh_token)
        # Here is where caching would go if we implement it
        return access_token

    def get_acr_refresh_token(self, aad_token, service_name):
        # type: (str, str) -> str
        # Here is where caching would go if we implement it
        return self.refresh_token_impl(
            "access_token",
            aad_token,
            None,
            service_name
        )