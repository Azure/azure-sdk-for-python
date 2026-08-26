# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from typing import Any, Optional, Tuple, TYPE_CHECKING
from urllib.parse import urlparse

from azure.core.exceptions import AzureError, HttpResponseError

from .models import StorageErrorCode
from .session import _analyze_request, _extract_session, Session, SessionCache
from .._blob_service_client import BlobServiceClient
from .._generated.models import CreateSessionConfiguration

if TYPE_CHECKING:
    from datetime import datetime
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import (
        PipelineRequest,
    )

_LOGGER = logging.getLogger(__name__)


def _to_service_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _is_cooldown_error(status: Optional[int], error_code: str) -> bool:
    if status is None:
        return False
    if status >= 500 or status == 403:
        return True
    return status == 400 and error_code == StorageErrorCode.FEATURE_NOT_ENABLED


class ContainerSessionProvider:
    """Creates, caches, and invalidates per-container sessions backed by a TokenCredential.

    A single provider may be shared across multiple clients to persist the session
    cache beyond the lifetime of any one of them. When no provider is supplied, each
    client creates one scoped to itself.

    :param str service_url: The blob service endpoint. Container and blob path segments
        and all query parameters are stripped.
    :param credential: The credential used to authorize CreateSession calls.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword str api_version: The Storage API version to use for CreateSession.
    """

    def __init__(self, service_url: str, credential: "TokenCredential", **kwargs: Any) -> None:
        if not hasattr(credential, "get_token"):
            raise TypeError(
                f"ContainerSessionProvider requires a TokenCredential; received {type(credential).__name__}."
            )
        self._client = BlobServiceClient(_to_service_url(service_url), credential=credential, **kwargs)
        self._cache = SessionCache()

    def is_request_eligible(self, request: "PipelineRequest") -> bool:
        """Checks whether the request can be signed with a session token.

        :param ~azure.core.pipeline.PipelineRequest request: The outgoing request.
        :return: True if the request is valid.
        :rtype: bool
        """
        return _analyze_request(request) is not None

    def get_session(self, request: "PipelineRequest") -> Optional[Session]:
        """Return a session, creating one on a miss.

        :param ~azure.core.pipeline.PipelineRequest request: The outgoing request.
        :return: A session, or None if the caller should use bearer auth.
        :rtype: ~azure.storage.blob._shared.session.Session or None
        """
        analyzed = _analyze_request(request)
        if analyzed is None:
            return None

        session = self._cache.get(analyzed[1])
        if session is None:
            session = self._acquire(analyzed)
        if session is None or session.is_fallback:
            return None
        return session

    def invalidate_session(self, request: "PipelineRequest", current: Session) -> None:
        """Drop the cached session if it still matches the rejected one.

        :param ~azure.core.pipeline.PipelineRequest request: The rejected request.
        :param current: The session that was rejected.
        :type current: ~azure.storage.blob._shared.session.Session
        """
        analyzed = _analyze_request(request)
        if analyzed is not None:
            self._cache.invalidate(analyzed[1], current.session_token)

    def _acquire(self, analyzed: Tuple[str, str]) -> Optional[Session]:
        container_name, container_url = analyzed
        with self._cache.lock_container(container_url):
            existing = self._cache.get(container_url)
            if existing is not None:
                return existing
            try:
                token, key, expires_at = self._create_session(container_name)
            except HttpResponseError as error:
                headers = getattr(error.response, "headers", {})
                error_code = headers.get("x-ms-error-code", "")
                if _is_cooldown_error(error.status_code, error_code):
                    _LOGGER.warning(
                        "CreateSession failed for container '%s' (HTTP %s, %s); "
                        "falling back to bearer for %d seconds.",
                        container_name,
                        error.status_code,
                        error_code,
                        int(self._cache.FALLBACK_COOLDOWN.total_seconds()),
                    )
                    self._cache.put_fallback(container_url)
                else:
                    _LOGGER.warning(
                        "CreateSession failed for container '%s'; using bearer for this request.",
                        container_name,
                        exc_info=True,
                    )
                return None
            except (AzureError, ValueError):
                _LOGGER.warning(
                    "CreateSession failed for container '%s'; using bearer for this request.",
                    container_name,
                    exc_info=True,
                )
                return None
            self._cache.put(container_url, token, key, expires_at)
            return self._cache.get(container_url)

    def _create_session(self, container_name: str) -> Tuple[str, str, "datetime"]:
        container_client = self._client.get_container_client(container_name)
        response = container_client._client.container.create_session(
            create_session_configuration=CreateSessionConfiguration(authentication_type="HMAC")
        )
        return _extract_session(response)
