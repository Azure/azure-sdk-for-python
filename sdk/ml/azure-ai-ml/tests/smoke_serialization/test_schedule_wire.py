# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Golden wire-serialization smoke tests for JobSchedule.

A schedule is the inverse-tree case: a msrest schedule envelope embeds a job definition. On a
migration branch the embedded job becomes an arm-hybrid child, so this guards the schedule embed-site.
See ``test_command_job_wire.py`` for the two-check pattern.
"""
import pytest

from _builders import SCHEDULE_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes


@pytest.mark.parametrize("case_name", sorted(SCHEDULE_BUILDERS))
def test_schedule_serializes(case_name):
    """The JobSchedule rest object must serialize to wire without raising (serialization guard)."""
    entity = SCHEDULE_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(SCHEDULE_BUILDERS))
def test_schedule_wire_matches_expected(case_name):
    """The JobSchedule wire must be byte-identical to the baseline captured from main."""
    entity = SCHEDULE_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
