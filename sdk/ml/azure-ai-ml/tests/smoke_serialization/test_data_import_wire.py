# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for data-import entities.

See ``test_command_job_wire.py`` for the two-check pattern (serialization guard + wire equivalence).
"""
import pytest

from _builders_data_import import DATA_IMPORT_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes


@pytest.mark.parametrize("case_name", sorted(DATA_IMPORT_BUILDERS))
def test_data_import_serializes(case_name):
    """The data-import rest object must serialize to wire without raising."""
    entity = DATA_IMPORT_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(DATA_IMPORT_BUILDERS))
def test_data_import_wire_matches_expected(case_name):
    """The data-import wire must be byte-identical to the baseline captured from main."""
    entity = DATA_IMPORT_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
