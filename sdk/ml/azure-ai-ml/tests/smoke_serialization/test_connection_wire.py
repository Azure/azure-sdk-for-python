# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for workspace-connection entities.

See ``test_command_job_wire.py`` for the two-check pattern (serialization guard + wire equivalence).
"""
import pytest

from _builders_connection import CONNECTION_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes


@pytest.mark.parametrize("case_name", sorted(CONNECTION_BUILDERS))
def test_connection_serializes(case_name):
    """The connection rest object must serialize to wire without raising."""
    entity = CONNECTION_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(CONNECTION_BUILDERS))
def test_connection_wire_matches_expected(case_name):
    """The connection wire must be byte-identical to the baseline captured from main."""
    entity = CONNECTION_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
