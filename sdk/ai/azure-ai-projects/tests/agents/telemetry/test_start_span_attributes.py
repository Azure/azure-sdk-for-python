# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for the request attributes that ``start_span`` records on a recording span.

These tests replace the tracing implementation with a mock span factory, so no
OpenTelemetry exporter or network access is needed.
"""

from unittest.mock import MagicMock, patch

from azure.ai.projects.telemetry import _utils
from azure.ai.projects.telemetry._utils import (
    GEN_AI_REQUEST_TEMPERATURE,
    GEN_AI_REQUEST_TOP_P,
    OperationName,
    start_span,
)


def _make_recording_span_factory():
    span = MagicMock()
    span.span_instance.is_recording = MagicMock(return_value=True)
    return MagicMock(return_value=span), span


class TestStartSpanAttributes:
    """Verify start_span records request parameters, including zero values."""

    def test_zero_temperature_and_top_p_are_recorded(self):
        factory, span = _make_recording_span_factory()

        with patch.object(_utils, "_span_impl_type", factory):
            start_span(OperationName.CREATE_AGENT, server_address="example.com", temperature=0.0, top_p=0.0)

        span.add_attribute.assert_any_call(GEN_AI_REQUEST_TEMPERATURE, "0.0")
        span.add_attribute.assert_any_call(GEN_AI_REQUEST_TOP_P, "0.0")

    def test_unset_temperature_and_top_p_are_not_recorded(self):
        factory, span = _make_recording_span_factory()

        with patch.object(_utils, "_span_impl_type", factory):
            start_span(OperationName.CREATE_AGENT, server_address="example.com")

        recorded_names = [call.args[0] for call in span.add_attribute.call_args_list]
        assert GEN_AI_REQUEST_TEMPERATURE not in recorded_names
        assert GEN_AI_REQUEST_TOP_P not in recorded_names
