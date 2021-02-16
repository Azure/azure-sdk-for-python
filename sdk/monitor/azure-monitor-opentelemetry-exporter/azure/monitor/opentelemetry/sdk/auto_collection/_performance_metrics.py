# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
from typing import Dict

import psutil
from opentelemetry.metrics import Meter, Observer

from azure.monitor.opentelemetry.sdk.auto_collection._utils import AutoCollectionType

logger = logging.getLogger(__name__)
PROCESS = psutil.Process()


class PerformanceMetrics:
    """Starts auto collection of performance metrics, including
    "Processor time as a percentage", "Amount of available memory
    in bytes", "Process CPU usage as a percentage" and "Amount of
    memory process has used in bytes" metrics.

    Args:
        meter: OpenTelemetry Meter
        labels: Dictionary of labels
        collection_type: Standard or Live Metrics
    """

    def __init__(
        self,
        meter: Meter,
        labels: Dict[str, str],
        collection_type: AutoCollectionType,
    ):
        self._meter = meter
        self._labels = labels

        self._meter.register_updownsumobserver(
            callback=self._track_cpu,
            name="\\Processor(_Total)\\% Processor Time",
            description="Processor time as a percentage",
            unit="percentage",
            value_type=float,
        )

        if collection_type == AutoCollectionType.PERF_COUNTER:
            self._meter.register_updownsumobserver(
                callback=self._track_memory,
                name="\\Memory\\Available Bytes",
                description="Amount of available memory in bytes",
                unit="byte",
                value_type=int,
            )
            self._meter.register_updownsumobserver(
                callback=self._track_process_cpu,
                name="\\Process(??APP_WIN32_PROC??)\\% Processor Time",
                description="Process CPU usage as a percentage",
                unit="percentage",
                value_type=float,
            )
            self._meter.register_updownsumobserver(
                callback=self._track_process_memory,
                name="\\Process(??APP_WIN32_PROC??)\\Private Bytes",
                description="Amount of memory process has used in bytes",
                unit="byte",
                value_type=int,
            )
        if collection_type == AutoCollectionType.LIVE_METRICS:
            self._meter.register_updownsumobserver(
                callback=self._track_commited_memory,
                name="\\Memory\\Committed Bytes",
                description="Amount of committed memory in bytes",
                unit="byte",
                value_type=int,
            )

    def _track_cpu(self, observer: Observer) -> None:
        """Track CPU time

        Processor time is defined as a float representing the current system
        wide CPU utilization minus idle CPU time as a percentage. Idle CPU
        time is defined as the time spent doing nothing. Return values range
        from 0.0 to 100.0 inclusive.
        """
        cpu_times_percent = psutil.cpu_times_percent()
        observer.observe(100.0 - cpu_times_percent.idle, self._labels)

    def _track_memory(self, observer: Observer) -> None:
        """Track Memory

        Available memory is defined as memory that can be given instantly to
        processes without the system going into swap.
        """
        observer.observe(psutil.virtual_memory().available, self._labels)

    def _track_process_cpu(self, observer: Observer) -> None:
        """Track Process CPU time

        Returns a derived gauge for the CPU usage for the current process.
        Return values range from 0.0 to 100.0 inclusive.
        """
        try:
            # In the case of a process running on multiple threads on different
            # CPU cores, the returned value of cpu_percent() can be > 100.0. We
            # normalize the cpu process using the number of logical CPUs
            cpu_count = psutil.cpu_count(logical=True)
            observer.observe(PROCESS.cpu_percent() / cpu_count, self._labels)
        except Exception:  # pylint: disable=broad-except
            logger.warning("Error handling get process cpu usage.")

    def _track_process_memory(self, observer: Observer) -> None:
        """Track Memory

         Available memory is defined as memory that can be given instantly to
        processes without the system going into swap.
        """
        try:
            observer.observe(PROCESS.memory_info().rss, self._labels)
        except Exception:  # pylint: disable=broad-except
            logger.warning("Error handling get process private bytes.")

    def _track_commited_memory(self, observer: Observer) -> None:
        """Track Commited Memory

        Available commited memory is defined as total memory minus available memory.
        """
        observer.observe(
            psutil.virtual_memory().total - psutil.virtual_memory().available,
            self._labels,
        )
