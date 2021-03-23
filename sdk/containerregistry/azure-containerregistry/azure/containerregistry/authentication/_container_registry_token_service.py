# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._container_registry_token_request_context import ContainerRegistryTokenRequestContext


class ContainerRegistryTokenService(object):
    """A token service for obtaining tokens to be used by the container registry service"""

    def __init__(self, token_credential, url, pipeline):
        self.token_service = TokenService(url, pipeline)
        self.refresh_cache = None  # TODO: decide on cache

    def get_token(self, req_context):
        # type: (ContainerRegistryTokenRequestContext) -> AccessToken
        scope = req_context.scope
        service_name = req_context.service_name

        refresh_token = self.refresh_cache.get_token(req_context)
        return self.token_service.get_acr_access_token(refresh_token, scope, service_name)
