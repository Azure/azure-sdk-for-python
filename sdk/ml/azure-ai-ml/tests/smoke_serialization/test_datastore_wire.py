# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for datastore entities.

See ``test_command_job_wire.py`` for the two-check pattern (serialization guard + wire equivalence).
"""
import pytest

from _builders_datastore import DATASTORE_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes


@pytest.mark.parametrize("case_name", sorted(DATASTORE_BUILDERS))
def test_datastore_serializes(case_name):
    """The datastore rest object must serialize to wire without raising."""
    entity = DATASTORE_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(DATASTORE_BUILDERS))
def test_datastore_wire_matches_expected(case_name):
    """The datastore wire must be byte-identical to the baseline captured from main."""
    entity = DATASTORE_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
