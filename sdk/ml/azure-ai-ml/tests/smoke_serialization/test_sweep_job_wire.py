# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Golden wire-serialization smoke tests for SweepJob.

See ``test_command_job_wire.py`` for the two-check pattern (serialize-smoke + golden equivalence).
"""
import pytest

from _builders import SWEEP_JOB_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes


@pytest.mark.parametrize("case_name", sorted(SWEEP_JOB_BUILDERS))
def test_sweep_job_serializes(case_name):
    """The SweepJob rest object must serialize to wire without raising (serialization guard)."""
    entity = SWEEP_JOB_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(SWEEP_JOB_BUILDERS))
def test_sweep_job_wire_matches_expected(case_name):
    """The SweepJob wire must be byte-identical to the baseline captured from main."""
    entity = SWEEP_JOB_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
