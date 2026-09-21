# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for the distillation job entity.

See ``test_command_job_wire.py`` for the two-check pattern (serialization guard + wire equivalence).
"""
import pytest

from _builders_distillation import DISTILLATION_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes


@pytest.mark.parametrize("case_name", sorted(DISTILLATION_BUILDERS))
def test_distillation_serializes(case_name):
    """The distillation rest object must serialize to wire without raising."""
    entity = DISTILLATION_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(DISTILLATION_BUILDERS))
def test_distillation_wire_matches_expected(case_name):
    """The distillation wire must be byte-identical to the baseline captured from main."""
    entity = DISTILLATION_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
