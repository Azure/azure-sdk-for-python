# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Golden wire-serialization smoke tests for SparkJob.

See ``test_command_job_wire.py`` for the two-check pattern (serialize-smoke + golden equivalence).
"""
import pytest

from _builders import SPARK_JOB_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes


@pytest.mark.parametrize("case_name", sorted(SPARK_JOB_BUILDERS))
def test_spark_job_serializes(case_name):
    """The SparkJob rest object must serialize to wire without raising (serialization guard)."""
    entity = SPARK_JOB_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(SPARK_JOB_BUILDERS))
def test_spark_job_wire_matches_expected(case_name):
    """The SparkJob wire must be byte-identical to the baseline captured from main."""
    entity = SPARK_JOB_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
