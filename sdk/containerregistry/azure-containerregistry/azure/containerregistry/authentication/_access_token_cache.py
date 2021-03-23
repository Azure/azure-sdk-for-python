# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._access_token import AccessToken
    from ._container_registry_token_credential import ContainerRegistryTokenCredential
    from ._container_registry_token_request_context import ContainerRegistryTokenRequestContext

logger = logging.getLogger()


class AccessTokenCacheImpl(object):
    """An access token cache that supports caching and refreshing a token"""

    # Delay after a refresh to attempt another refresh token
    _refresh_delay = 30
    # Offset before token expiry to attempt proactive token refresh
    _refresh_offset = 300

    def __init__(self, token_credential):
        # type: (ContainerRegistryTokenCredential) -> None
        self._token_credential = token_credential
        self.should_refresh = True

    def get_token(self, token_request_context):
        # type: (ContainerRegistryTokenContext) -> AccessToken
        self.retrieve_token(token_request_context)

    def retrieve_token(self, token_request_context):
        # type: (ContainerRegistryTokenContext) -> AccessToken
        # Caching implementation will go here

        token_refresh = self._token_credential.get_token(token_request_context)

        return token_refresh

    def _check_if_force_refresh(self, token_request_context):
        # type: (ContainerRegistryTokenContext) -> bool
        # TODO: Add caching in later previews
        return True

    def _process_token_refresh(self, now, fallback):
        # type: (datetime, AccessToken) -> AccessToken
        return fallback

    def refresh_log(self, cache, now, log):
        # type: (AccessToken, datetime, str) -> str
        if not cache:
            return "."
        return "Retry may be attempted after {} seconds.".format(self._refresh_delay)
