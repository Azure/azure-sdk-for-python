# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Golden wire-serialization smoke tests for CommandJob.

Two checks per case, both branch-agnostic (identical on pre-migration ``main`` and on any migration
branch):

1. **serialize-smoke (Class A)** — ``entity._to_rest_object()`` serializes to JSON without raising.
2. **golden wire-equivalence (Class B)** — the produced wire equals the golden captured from ``main``.

Run (offline, no Azure, no recordings):

    cd sdk/ml/azure-ai-ml/tests/smoke_serialization
    python -m pytest test_command_job_wire.py -v
"""
import pytest

from _builders import COMMAND_JOB_BUILDERS
from _wire import assert_matches_golden, assert_serializes


@pytest.mark.parametrize("golden_name", sorted(COMMAND_JOB_BUILDERS))
def test_command_job_serializes(golden_name):
    """The CommandJob rest object must serialize to wire without raising (Class A guard)."""
    entity = COMMAND_JOB_BUILDERS[golden_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("golden_name", sorted(COMMAND_JOB_BUILDERS))
def test_command_job_wire_matches_golden(golden_name):
    """The CommandJob wire must be byte-identical to the golden captured from main (Class B guard)."""
    entity = COMMAND_JOB_BUILDERS[golden_name]()
    assert_matches_golden(golden_name, entity._to_rest_object())
