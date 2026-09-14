# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for online/batch endpoint + deployment entities.

See ``test_command_job_wire.py`` for the two-check pattern (serialization guard + wire equivalence).
"""
import pytest

from _builders_endpoint import BATCH_ENDPOINT_BUILDERS, ONLINE_ENDPOINT_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes

_ALL = {}
_ALL.update(ONLINE_ENDPOINT_BUILDERS)
_ALL.update(BATCH_ENDPOINT_BUILDERS)


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_endpoint_serializes(case_name):
    """The endpoint/deployment rest object must serialize to wire without raising."""
    entity = _ALL[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_endpoint_wire_matches_expected(case_name):
    """The endpoint/deployment wire must be byte-identical to the baseline captured from main."""
    entity = _ALL[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
