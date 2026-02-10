# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=arguments-renamed,docstring-missing-return,docstring-missing-rtype

import logging
from typing import Optional

from azure.ai.ml._restclient.v2022_05_01.models import BatchRetrySettings as RestBatchRetrySettings
from azure.ai.ml._restclient.v2024_04_01_dataplanepreview.models import (
    OnlineRequestSettings as RestOnlineRequestSettings,
)
from azure.ai.ml._restclient.v2024_04_01_dataplanepreview.models import ProbeSettings as RestProbeSettings
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import (
    from_iso_duration_format,
    from_iso_duration_format_ms,
    to_iso_duration_format,
    to_iso_duration_format_ms,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin

module_logger = logging.getLogger(__name__)


@experimental
class BatchRetrySettings(RestTranslatableMixin):
    """Retry settings for batch deployment.

    :param max_retries: Number of retries in failure, defaults to 3
    :type max_retries: int
    :param timeout: Timeout in seconds, defaults to 30
    :type timeout: int
    """

    def __init__(self, *, max_retries: Optional[int] = None, timeout: Optional[int] = None):
        self.max_retries = max_retries
        self.timeout = timeout

    def _to_rest_object(self) -> RestBatchRetrySettings:
        return RestBatchRetrySettings(
            max_retries=self.max_retries,
            timeout=to_iso_duration_format(self.timeout),
        )

    @classmethod
    def _from_rest_object(cls, settings: RestBatchRetrySettings) -> Optional["BatchRetrySettings"]:
        return (
            BatchRetrySettings(
                max_retries=settings.max_retries,
                timeout=from_iso_duration_format(settings.timeout),
            )
            if settings
            else None
        )

    def _merge_with(self, other: "BatchRetrySettings") -> None:
        if other:
            self.timeout = other.timeout or self.timeout
            self.max_retries = other.max_retries or self.max_retries


@experimental
class OnlineRequestSettings(RestTranslatableMixin):
    """Request Settings entity.

    :param request_timeout_ms: defaults to 5000
    :type request_timeout_ms: int
    :param max_concurrent_requests_per_instance: defaults to 1
    :type max_concurrent_requests_per_instance: int
    """

    def __init__(
        self,
        max_concurrent_requests_per_instance: Optional[int] = None,
        request_timeout_ms: Optional[int] = None,
    ):
        self.request_timeout_ms = request_timeout_ms
        self.max_concurrent_requests_per_instance = max_concurrent_requests_per_instance

    def _to_rest_object(self) -> RestOnlineRequestSettings:
        return RestOnlineRequestSettings(
            max_concurrent_requests_per_instance=self.max_concurrent_requests_per_instance,
            request_timeout=to_iso_duration_format_ms(self.request_timeout_ms),
        )

    def _to_dict(self) -> dict:
        """Convert to plain dictionary for API request body."""
        result = {}
        if self.max_concurrent_requests_per_instance is not None:
            result["maxConcurrentRequestsPerInstance"] = self.max_concurrent_requests_per_instance
        if self.request_timeout_ms is not None:
            result["requestTimeout"] = to_iso_duration_format_ms(self.request_timeout_ms)
        return result

    def _merge_with(self, other: Optional["OnlineRequestSettings"]) -> None:
        if other:
            self.max_concurrent_requests_per_instance = (
                other.max_concurrent_requests_per_instance or self.max_concurrent_requests_per_instance
            )
            self.request_timeout_ms = other.request_timeout_ms or self.request_timeout_ms

    @classmethod
    def _from_rest_object(cls, settings: RestOnlineRequestSettings) -> Optional["OnlineRequestSettings"]:
        return (
            OnlineRequestSettings(
                request_timeout_ms=from_iso_duration_format_ms(settings.request_timeout),
                max_concurrent_requests_per_instance=settings.max_concurrent_requests_per_instance,
            )
            if settings
            else None
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OnlineRequestSettings):
            return NotImplemented
        if not other:
            return False
        # only compare mutable fields
        return (
            self.max_concurrent_requests_per_instance == other.max_concurrent_requests_per_instance
            and self.request_timeout_ms == other.request_timeout_ms
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


@experimental
class ProbeSettings(RestTranslatableMixin):
    def __init__(
        self,
        *,
        failure_threshold: Optional[int] = None,
        success_threshold: Optional[int] = None,
        timeout: Optional[int] = None,
        period: Optional[int] = None,
        initial_delay: Optional[int] = None,
        scheme: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """Settings on how to probe an endpoint.

        :param failure_threshold: Threshold for probe failures, defaults to 30
        :type failure_threshold: int
        :param success_threshold: Threshold for probe success, defaults to 1
        :type success_threshold: int
        :param timeout: timeout in seconds, defaults to 2
        :type timeout: int
        :param period: How often (in seconds) to perform the probe, defaults to 10
        :type period: int
        :param initial_delay: How long (in seconds) to wait for the first probe, defaults to 10
        :type initial_delay: int
        """

        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.period = period
        self.initial_delay = initial_delay
        self.scheme = scheme
        self.method = method
        self.path = path
        self.port = port

    def _to_rest_object(self) -> RestProbeSettings:
        return RestProbeSettings(
            failure_threshold=self.failure_threshold,
            success_threshold=self.success_threshold,
            timeout=to_iso_duration_format(self.timeout),
            period=to_iso_duration_format(self.period),
            initial_delay=to_iso_duration_format(self.initial_delay),
            scheme=self.scheme,
            http_method=self.method,  # REST client expects http_method, not method
            path=self.path,
            port=self.port,
        )  # type: ignore

    def _to_dict(self) -> dict:
        """Convert to plain dictionary for API request body."""
        result = {}
        if self.failure_threshold is not None:
            result["failureThreshold"] = self.failure_threshold
        if self.success_threshold is not None:
            result["successThreshold"] = self.success_threshold
        if self.timeout is not None:
            result["timeout"] = to_iso_duration_format(self.timeout)
        if self.period is not None:
            result["period"] = to_iso_duration_format(self.period)
        if self.initial_delay is not None:
            result["initialDelay"] = to_iso_duration_format(self.initial_delay)
        if self.scheme is not None:
            result["scheme"] = self.scheme  # type: ignore
        if self.method is not None:
            result["httpMethod"] = self.method  # type: ignore
        if self.path is not None:
            result["path"] = self.path  # type: ignore[assignment]
        if self.port is not None:
            result["port"] = self.port  # type: ignore[assignment]
        return result

    def _merge_with(self, other: Optional["ProbeSettings"]) -> None:
        if other:
            self.failure_threshold = other.failure_threshold or self.failure_threshold
            self.success_threshold = other.success_threshold or self.success_threshold
            self.timeout = other.timeout or self.timeout
            self.period = other.period or self.period
            self.initial_delay = other.initial_delay or self.initial_delay
            self.scheme = other.scheme or self.scheme
            self.method = other.method or self.method
            self.path = other.path or self.path
            self.port = other.port or self.port

    @classmethod
    def _from_rest_object(cls, settings: RestProbeSettings) -> Optional["ProbeSettings"]:
        return (
            ProbeSettings(
                failure_threshold=settings.failure_threshold,
                success_threshold=settings.success_threshold,
                timeout=from_iso_duration_format(settings.timeout),
                period=from_iso_duration_format(settings.period),
                initial_delay=from_iso_duration_format(settings.initial_delay),
                scheme=settings.scheme,
                method=settings.http_method,
                path=settings.path,
                port=settings.port,
            )
            if settings
            else None
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProbeSettings):
            return NotImplemented
        if not other:
            return False
        # only compare mutable fields
        return (
            self.failure_threshold == other.failure_threshold
            and self.success_threshold == other.success_threshold
            and self.timeout == other.timeout
            and self.period == other.period
            and self.initial_delay == other.initial_delay
            and self.scheme == other.scheme
            and self.method == other.method
            and self.path == other.path
            and self.port == other.port
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
