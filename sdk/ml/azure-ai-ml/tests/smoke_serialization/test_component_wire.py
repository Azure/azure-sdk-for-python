# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for component entities (Command, Spark)."""
import pytest

from _builders_component import COMMAND_COMPONENT_BUILDERS, SPARK_COMPONENT_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes

_ALL = {}
_ALL.update(COMMAND_COMPONENT_BUILDERS)
_ALL.update(SPARK_COMPONENT_BUILDERS)


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_component_serializes(case_name):
    """The component rest object must serialize to wire without raising."""
    entity = _ALL[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_component_wire_matches_expected(case_name):
    """The component wire must be byte-identical to the baseline captured from main."""
    entity = _ALL[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
