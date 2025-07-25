# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import math
import threading
import time
from typing import Optional, Sequence
from opentelemetry.context import Context
from opentelemetry.trace import Link, SpanKind, format_trace_id
from opentelemetry.sdk.trace.sampling import (
    Decision,
    Sampler,
    SamplingResult,
    _get_parent_trace_state,
)
from opentelemetry.trace.span import TraceState
from opentelemetry.util.types import Attributes

from azure.monitor.opentelemetry.exporter._constants import _SAMPLE_RATE_KEY

from azure.monitor.opentelemetry.exporter.export.trace._utils import (
    _get_DJB2_sample_score,
    _round_down_to_nearest,
    parent_context_sampling,
)

class _State:
    def __init__(self, effective_window_count: float, effective_window_nanoseconds: float, last_nano_time: int):
        self.effective_window_count = effective_window_count
        self.effective_window_nanoseconds = effective_window_nanoseconds
        self.last_nano_time = last_nano_time

class RateLimitedSamplingPercentage:
    def __init__(self, target_spans_per_second_limit: float, round_to_nearest: bool = True):
        if target_spans_per_second_limit < 0.0:
            raise ValueError("Limit for sampled spans per second must be nonnegative!")
        # Hardcoded adaptation time of 0.1 seconds for adjusting to sudden changes in telemetry volumes
        adaptation_time_seconds = 0.1
        self._inverse_adaptation_time_nanoseconds = 1e-9 / adaptation_time_seconds
        self._target_spans_per_nanosecond_limit = 1e-9 * target_spans_per_second_limit
        initial_nano_time = int(time.time_ns())
        self._state = _State(0.0, 0.0, initial_nano_time)
        self._lock = threading.Lock()
        self._round_to_nearest = round_to_nearest

    def _update_state(self, old_state: _State, current_nano_time: int) -> _State:
        if current_nano_time <= old_state.last_nano_time:
            return _State(
                old_state.effective_window_count + 1,
                old_state.effective_window_nanoseconds,
                old_state.last_nano_time
            )
        nano_time_delta = current_nano_time - old_state.last_nano_time
        decay_factor = math.exp(-nano_time_delta * self._inverse_adaptation_time_nanoseconds)
        current_effective_window_count = old_state.effective_window_count * decay_factor + 1
        current_effective_window_nanoseconds = old_state.effective_window_nanoseconds * decay_factor + nano_time_delta

        return _State(current_effective_window_count, current_effective_window_nanoseconds, current_nano_time)

    def get(self) -> float:
        current_nano_time = int(time.time_ns())

        with self._lock:
            old_state = self._state
            self._state = self._update_state(old_state, current_nano_time)
            current_state = self._state

        # Calculate sampling probability based on current state
        if current_state.effective_window_count == 0:
            return 100.0

        sampling_probability = (
            (current_state.effective_window_nanoseconds * self._target_spans_per_nanosecond_limit) /
            current_state.effective_window_count
        )

        sampling_percentage = 100 * min(sampling_probability, 1.0)

        if self._round_to_nearest:
            sampling_percentage = _round_down_to_nearest(sampling_percentage)

        return sampling_percentage


class RateLimitedSampler(Sampler):
    def __init__(self, target_spans_per_second_limit: float):
        self._sampling_percentage_generator = RateLimitedSamplingPercentage(target_spans_per_second_limit)
        self._description = f"RateLimitedSampler{{{target_spans_per_second_limit}}}"

    def should_sample(
        self,
        parent_context: Optional[Context],
        trace_id: int,
        name: str,
        kind: Optional[SpanKind] = None,
        attributes: Attributes = None,
        links: Optional[Sequence["Link"]] = None,
        trace_state: Optional["TraceState"] = None,
    ) -> "SamplingResult":

        if parent_context is not None:
            parent_result = parent_context_sampling(parent_context, attributes)
            if parent_result is not None:
                return parent_result

        sampling_percentage = self._sampling_percentage_generator.get()
        sampling_score = _get_DJB2_sample_score(format_trace_id(trace_id).lower()) * 100.0

        if sampling_score < sampling_percentage:
            decision = Decision.RECORD_AND_SAMPLE
        else:
            decision = Decision.DROP

        if sampling_percentage == 100.0:
            new_attributes = {}
        else:
            new_attributes = {} if attributes is None else dict(attributes)
            new_attributes[_SAMPLE_RATE_KEY] = sampling_percentage

        return SamplingResult(
            decision,
            new_attributes,
            _get_parent_trace_state(parent_context),
        )

    def get_description(self) -> str:
        return self._description
