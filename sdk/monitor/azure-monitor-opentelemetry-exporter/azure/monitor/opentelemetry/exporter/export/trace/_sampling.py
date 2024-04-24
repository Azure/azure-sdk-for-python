# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Optional, Sequence

# pylint:disable=no-name-in-module
from fixedint import Int32
# pylint:disable=W0611
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


_HASH = 5381
_INTEGER_MAX: int = Int32.maxval
_INTEGER_MIN: int = Int32.minval


# Sampler is responsible for the following:
# Implements same trace id hashing algorithm so that traces are sampled the same across multiple nodes (via AI SDKS)
# Adds item count to span attribute if span is sampled (needed for ingestion service)
# Inherits from the Sampler interface as defined by OpenTelemetry
# https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/sdk.md#sampler
class ApplicationInsightsSampler(Sampler):
    """Sampler that implements the same probability sampling algorithm as the ApplicationInsights SDKs."""

    # sampling_ratio must take a value in the range [0,1]
    def __init__(self, sampling_ratio: float = 1.0):
        if not 0.0 <= sampling_ratio <= 1.0:
            raise ValueError("sampling_ratio must be in the range [0,1]")
        self._ratio = sampling_ratio
        self._sample_rate = sampling_ratio * 100

    # pylint:disable=C0301
    # See https://github.com/microsoft/Telemetry-Collection-Spec/blob/main/OpenTelemetry/trace/ApplicationInsightsSampler.md
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
        if self._sample_rate == 0:
            decision = Decision.DROP
        elif self._sample_rate == 100.0:
            decision = Decision.RECORD_AND_SAMPLE
        else:
            # Determine if should sample from ratio and traceId
            sample_score = self._get_DJB2_sample_score(format_trace_id(trace_id).lower())
            if sample_score < self._ratio:
                decision = Decision.RECORD_AND_SAMPLE
            else:
                decision = Decision.DROP
        # Add sample rate as span attribute
        if attributes is None:
            attributes = {}
        attributes[_SAMPLE_RATE_KEY] = self._sample_rate # type: ignore
        return SamplingResult(
            decision,
            attributes,
            _get_parent_trace_state(parent_context), # type: ignore
        )

    def _get_DJB2_sample_score(self, trace_id_hex: str) -> float:
        # This algorithm uses 32bit integers
        hash_value = Int32(_HASH)
        for char in trace_id_hex:
            hash_value = ((hash_value << 5) + hash_value) + ord(char)

        if hash_value == _INTEGER_MIN:
            hash_value = int(_INTEGER_MAX)
        else:
            hash_value = abs(hash_value)

        # divide by _INTEGER_MAX for value between 0 and 1 for sampling score
        return float(hash_value) / _INTEGER_MAX


    def get_description(self) -> str:
        return "ApplicationInsightsSampler{}".format(self._ratio)


def azure_monitor_opentelemetry_sampler_factory(sampler_argument):  # pylint: disable=name-too-long
    try:
        rate = float(sampler_argument)
        return ApplicationInsightsSampler(rate)
    except (ValueError, TypeError):
        return ApplicationInsightsSampler()
