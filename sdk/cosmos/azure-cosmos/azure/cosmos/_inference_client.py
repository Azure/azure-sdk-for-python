# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Client-owned settings and lazy initialization for the separate inference service."""

from dataclasses import dataclass
from threading import Lock
from typing import Callable, Generic, Optional, TypeVar, Union

from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import AsyncHTTPPolicy, HTTPPolicy
from urllib3.util.retry import Retry

from .exceptions import CosmosHttpResponseError
from .http_constants import StatusCodes

_ServiceT = TypeVar("_ServiceT")
_CredentialT = TypeVar("_CredentialT", TokenCredential, AsyncTokenCredential)


@dataclass(frozen=True)
class InferenceClientSettings(Generic[_CredentialT]):
    """Inference configuration prepared by CosmosClient, without a connection."""

    aad_credentials: Optional[_CredentialT]
    request_timeout: float
    retry_configuration: Optional[Union[HTTPPolicy, AsyncHTTPPolicy, int, Retry]]
    user_agent: str
    enable_diagnostics_logging: bool


class InferenceClient(Generic[_CredentialT, _ServiceT]):
    """Share one lazily created inference service across a client's proxies."""

    def __init__(
        self,
        settings: InferenceClientSettings[_CredentialT],
        service_factory: Callable[[InferenceClientSettings[_CredentialT]], _ServiceT],
    ) -> None:
        self._settings: InferenceClientSettings[_CredentialT] = settings
        self._service_factory: Callable[[InferenceClientSettings[_CredentialT]], _ServiceT] = service_factory
        self._service: Optional[_ServiceT] = None
        self._lock = Lock()

    def get_service(self) -> Optional[_ServiceT]:
        """Create on first use; construction is synchronous for both service types."""
        if self._service is None and self._settings.aad_credentials:
            with self._lock:
                if self._service is None:
                    try:
                        self._service = self._service_factory(self._settings)
                    except ValueError as exc:
                        raise CosmosHttpResponseError(
                            message=f"Failed to initialize inference service: {exc}",
                            response=None,
                            status_code=StatusCodes.BAD_REQUEST,
                        ) from exc
        return self._service
