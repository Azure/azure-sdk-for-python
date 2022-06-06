# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azure.ai.ml._restclient.v2021_10_01.models import (
    OnlineRequestSettings as RestOnlineRequestSettings,
    ProbeSettings as RestProbeSettings,
    BatchRetrySettings as RestBatchRetrySettings,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils.utils import (
    to_iso_duration_format,
    from_iso_duration_format,
    to_iso_duration_format_ms,
    from_iso_duration_format_ms,
)

module_logger = logging.getLogger(__name__)


class BatchRetrySettings(RestTranslatableMixin):
    """Retry settings for batch deployment

    :param max_retries: Number of retries in failure, defaults to 3
    :type max_retries: int, optional
    :param timeout: Timeout in seconds, defaults to 30
    :type timeout: int, optional
    """

    def __init__(self, *, max_retries: int = None, timeout: int = None):
        self.max_retries = max_retries
        self.timeout = timeout

    def _to_rest_object(self) -> RestBatchRetrySettings:
        return RestBatchRetrySettings(
            max_retries=self.max_retries,
            timeout=to_iso_duration_format(self.timeout),
        )

    @classmethod
    def _from_rest_object(cls, settings: RestBatchRetrySettings) -> "BatchRetrySettings":

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


class OnlineRequestSettings(RestTranslatableMixin):
    """Reqeust Settings entity

    :param request_timeout_ms: defaults to 5000
    :type request_timeout_ms: int, optional
    :param max_concurrent_requests_per_instance: defaults to 1
    :type max_concurrent_requests_per_instance: int, optional
    :param max_queue_wait_ms: defaults to 500
    :type max_queue_wait_ms: int, optional
    """

    def __init__(
        self,
        max_concurrent_requests_per_instance: int = None,
        request_timeout_ms: int = None,
        max_queue_wait_ms: int = None,
    ):
        self.request_timeout_ms = request_timeout_ms
        self.max_concurrent_requests_per_instance = max_concurrent_requests_per_instance
        self.max_queue_wait_ms = max_queue_wait_ms

    def _to_rest_object(self) -> RestOnlineRequestSettings:
        return RestOnlineRequestSettings(
            max_queue_wait=to_iso_duration_format_ms(self.max_queue_wait_ms),
            max_concurrent_requests_per_instance=self.max_concurrent_requests_per_instance,
            request_timeout=to_iso_duration_format_ms(self.request_timeout_ms),
        )

    def _merge_with(self, other: "OnlineRequestSettings") -> None:
        if other:
            self.max_concurrent_requests_per_instance = (
                other.max_concurrent_requests_per_instance or self.max_concurrent_requests_per_instance
            )
            self.request_timeout_ms = other.request_timeout_ms or self.request_timeout_ms
            self.max_queue_wait_ms = other.max_queue_wait_ms or self.max_queue_wait_ms

    @classmethod
    def _from_rest_object(cls, settings: RestOnlineRequestSettings) -> "OnlineRequestSettings":

        return (
            OnlineRequestSettings(
                request_timeout_ms=from_iso_duration_format_ms(settings.request_timeout),
                max_concurrent_requests_per_instance=settings.max_concurrent_requests_per_instance,
                max_queue_wait_ms=from_iso_duration_format_ms(settings.max_queue_wait),
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
            and self.max_queue_wait_ms == other.max_queue_wait_ms
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class ProbeSettings(RestTranslatableMixin):
    def __init__(
        self,
        *,
        failure_threshold: int = None,
        success_threshold: int = None,
        timeout: int = None,
        period: int = None,
        initial_delay: int = None,
    ):
        """Settings on how to probe an endpoint

        :param failure_threshold: Threshold for probe failures, defaults to 30
        :type failure_threshold: int, optional
        :param success_threshold: Threshold for probe success, defaults to 1
        :type success_threshold: int, optional
        :param timeout: timeout in seconds, defaults to 2
        :type timeout: int, optional
        :param period: [description], defaults to 10
        :type period: int, optional
        :param initial_delay: How to to wait for the first probe, defaults to 10
        :type initial_delay: int, optional
        """

        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.period = period
        self.initial_delay = initial_delay

    def _to_rest_object(self) -> RestProbeSettings:
        return RestProbeSettings(
            failure_threshold=self.failure_threshold,
            success_threshold=self.success_threshold,
            timeout=to_iso_duration_format(self.timeout),
            period=to_iso_duration_format(self.period),
            initial_delay=to_iso_duration_format(self.initial_delay),
        )

    def _merge_with(self, other: "ProbeSettings") -> None:
        if other:
            self.failure_threshold = other.failure_threshold or self.failure_threshold
            self.success_threshold = other.success_threshold or self.success_threshold
            self.timeout = other.timeout or self.timeout
            self.period = other.period or self.period
            self.initial_delay = other.initial_delay or self.initial_delay

    @classmethod
    def _from_rest_object(cls, settings: RestProbeSettings) -> "ProbeSettings":
        return (
            ProbeSettings(
                failure_threshold=settings.failure_threshold,
                success_threshold=settings.success_threshold,
                timeout=from_iso_duration_format(settings.timeout),
                period=from_iso_duration_format(settings.period),
                initial_delay=from_iso_duration_format(settings.initial_delay),
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
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
