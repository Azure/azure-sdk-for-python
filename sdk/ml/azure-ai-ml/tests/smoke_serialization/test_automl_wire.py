# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for AutoML job entities."""
import pytest

from _builders_automl import AUTOML_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes


@pytest.mark.parametrize("case_name", sorted(AUTOML_BUILDERS))
def test_automl_serializes(case_name):
    """The AutoML rest object must serialize to wire without raising."""
    entity = AUTOML_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(AUTOML_BUILDERS))
def test_automl_wire_matches_expected(case_name):
    """The AutoML wire must be byte-identical to the baseline captured from main."""
    entity = AUTOML_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
