# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for the pipeline job entity.

See ``test_command_job_wire.py`` for the two-check pattern (serialization guard + wire equivalence).
"""
import pytest

from _builders_pipeline import PIPELINE_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes


@pytest.mark.parametrize("case_name", sorted(PIPELINE_BUILDERS))
def test_pipeline_serializes(case_name):
    """The pipeline rest object must serialize to wire without raising."""
    entity = PIPELINE_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(PIPELINE_BUILDERS))
def test_pipeline_wire_matches_expected(case_name):
    """The pipeline wire must be byte-identical to the baseline captured from main."""
    entity = PIPELINE_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
