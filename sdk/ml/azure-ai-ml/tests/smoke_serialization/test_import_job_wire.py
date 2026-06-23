# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Golden wire-serialization smoke tests for ImportJob.

See ``test_command_job_wire.py`` for the two-check pattern (serialize-smoke + golden equivalence).
"""
import pytest

from _builders import IMPORT_JOB_BUILDERS
from _wire import assert_matches_golden, assert_serializes


@pytest.mark.parametrize("golden_name", sorted(IMPORT_JOB_BUILDERS))
def test_import_job_serializes(golden_name):
    """The ImportJob rest object must serialize to wire without raising (Class A guard)."""
    entity = IMPORT_JOB_BUILDERS[golden_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("golden_name", sorted(IMPORT_JOB_BUILDERS))
def test_import_job_wire_matches_golden(golden_name):
    """The ImportJob wire must be byte-identical to the golden captured from main (Class B guard)."""
    entity = IMPORT_JOB_BUILDERS[golden_name]()
    assert_matches_golden(golden_name, entity._to_rest_object())
