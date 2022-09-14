# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Optional, Sequence

from fixedint import Int32
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


_HASH = 5381
_INTEGER_MAX = Int32.maxval
_INTEGER_MIN = Int32.minval


# Sampler is responsible for the following:
# Implements same trace id hashing algorithm so that traces are sampled the same across multiple nodes (via AI SDKS)
# Adds item count to span attribute if span is sampled (needed for ingestion service)
class ApplicationInsightsSampler(Sampler):
    """Sampler that implements the same probability sampling algorithm as the ApplicationInsights SDKs."""

    # sampling_ratio takes values in the range [0,1]
    def __init__(self, sampling_ratio: float = 1.0):
        self._ratio = sampling_ratio
        self._sample_rate = round(sampling_ratio * 100)

    # See https://github.com/microsoft/Telemetry-Collection-Spec/blob/main/OpenTelemetry/trace/ApplicationInsightsSampler.md
    def should_sample(
        self,
        parent_context: Optional["Context"],
        trace_id: int,
        name: str,
        kind: SpanKind = None,
        attributes: Attributes = None,
        links: Sequence["Link"] = None,
        trace_state: "TraceState" = None,
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
        attributes["sampleRate"] = self._sample_rate
        print(decision.name)
        return SamplingResult(
            decision,
            attributes,
            _get_parent_trace_state(parent_context),
        )

    def _get_DJB2_sample_score(self, trace_id_hex: str) -> int:
        # This algorithm uses 32bit integers
        hash = Int32(_HASH)
        for char in trace_id_hex:
            hash = ((hash << 5) + hash) + ord(char)
        
        if hash == _INTEGER_MIN:
            hash = int(_INTEGER_MAX)
        else:
            hash = abs(hash)

        # divide by _INTEGER_MAX for value between 0 and 1 for sampling score
        return float(hash) / _INTEGER_MAX


    def get_description(self) -> str:
        return "ApplicationInsightsSampler{}".format(self._ratio)
