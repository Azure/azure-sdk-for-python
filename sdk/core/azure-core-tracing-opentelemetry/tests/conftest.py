# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from opentelemetry import trace
from opentelemetry.sdk.trace import Tracer

import pytest


@pytest.fixture(scope="session")
def tracer():
    trace.set_preferred_tracer_implementation(lambda T: Tracer())
    return trace.tracer()
