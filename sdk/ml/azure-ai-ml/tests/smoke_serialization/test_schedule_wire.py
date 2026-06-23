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
from _wire import assert_matches_golden, assert_serializes


@pytest.mark.parametrize("golden_name", sorted(SCHEDULE_BUILDERS))
def test_schedule_serializes(golden_name):
    """The JobSchedule rest object must serialize to wire without raising (Class A guard)."""
    entity = SCHEDULE_BUILDERS[golden_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("golden_name", sorted(SCHEDULE_BUILDERS))
def test_schedule_wire_matches_golden(golden_name):
    """The JobSchedule wire must be byte-identical to the golden captured from main (Class B guard)."""
    entity = SCHEDULE_BUILDERS[golden_name]()
    assert_matches_golden(golden_name, entity._to_rest_object())
