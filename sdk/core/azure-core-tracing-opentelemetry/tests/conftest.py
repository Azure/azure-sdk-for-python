# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerSource

import pytest


@pytest.fixture(scope="session")
def tracer():
    trace.set_preferred_tracer_source_implementation(lambda T: TracerSource())
    return trace.tracer_source()
