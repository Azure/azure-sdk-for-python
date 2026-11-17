# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for monitoring (MonitorSchedule) entities."""
import pytest

from _builders_monitoring import MONITORING_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes

_ALL = {}
_ALL.update(MONITORING_BUILDERS)


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_monitoring_serializes(case_name):
    """The monitoring rest object must serialize to wire without raising."""
    entity = _ALL[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_monitoring_wire_matches_expected(case_name):
    """The monitoring wire must be byte-identical to the captured pre-migration baseline."""
    entity = _ALL[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
