# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
import sys

import pytest


@pytest.fixture(scope="session")
def tracer():
    trace.set_tracer_provider(TracerProvider())
    return trace.get_tracer(__name__)
