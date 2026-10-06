# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for serverless-endpoint and marketplace-subscription entities.

See ``test_command_job_wire.py`` for the two-check pattern (serialization guard + wire equivalence).
"""
import pytest

from _builders_serverless import SERVERLESS_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes


@pytest.mark.parametrize("case_name", sorted(SERVERLESS_BUILDERS))
def test_serverless_serializes(case_name):
    """The rest object must serialize to wire without raising."""
    entity = SERVERLESS_BUILDERS[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(SERVERLESS_BUILDERS))
def test_serverless_wire_matches_expected(case_name):
    """The wire must be byte-identical to the baseline captured from main."""
    entity = SERVERLESS_BUILDERS[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
