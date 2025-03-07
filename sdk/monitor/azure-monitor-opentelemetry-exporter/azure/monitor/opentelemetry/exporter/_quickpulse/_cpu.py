# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable

from datetime import datetime
from typing import Iterable

import psutil

from opentelemetry.metrics import CallbackOptions, Observation

from azure.monitor.opentelemetry.exporter._quickpulse._state import (
    _get_quickpulse_last_process_cpu,
    _get_quickpulse_last_process_time,
    _get_quickpulse_process_elapsed_time,
    _set_quickpulse_last_process_cpu,
    _set_quickpulse_last_process_time,
    _set_quickpulse_process_elapsed_time,
)

PROCESS = psutil.Process()
NUM_CPUS = psutil.cpu_count()


#  pylint: disable=unused-argument
def _get_process_memory(options: CallbackOptions) -> Iterable[Observation]:
    memory = 0
    try:
        # rss is non-swapped physical memory a process has used
        memory = PROCESS.memory_info().rss
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    yield Observation(memory, {})


# pylint: disable=unused-argument
def _get_process_time_normalized_old(options: CallbackOptions) -> Iterable[Observation]:
    normalized_cpu_percentage = 0.0
    try:
        cpu_times = PROCESS.cpu_times()
        # total process time is user + system in s
        total_time_s = cpu_times.user + cpu_times.system
        process_time_s = total_time_s - _get_quickpulse_last_process_time()
        _set_quickpulse_last_process_time(process_time_s)
        # Find elapsed time in s since last collection
        current_time = datetime.now()
        elapsed_time_s = (current_time - _get_quickpulse_process_elapsed_time()).total_seconds()
        _set_quickpulse_process_elapsed_time(current_time)
        # Obtain cpu % by dividing by elapsed time
        cpu_percentage = process_time_s / elapsed_time_s
        # Normalize by dividing by amount of logical cpus
        normalized_cpu_percentage = cpu_percentage / NUM_CPUS
        _set_quickpulse_last_process_cpu(normalized_cpu_percentage)
    except (psutil.NoSuchProcess, psutil.AccessDenied, ZeroDivisionError):
        pass
    yield Observation(normalized_cpu_percentage, {})


# pylint: disable=unused-argument
def _get_process_time_normalized(options: CallbackOptions) -> Iterable[Observation]:
    yield Observation(_get_quickpulse_last_process_cpu(), {})

# cSpell:enable
