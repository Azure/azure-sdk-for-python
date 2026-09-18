# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for asset entities (Model, Environment, Data, Code).

See ``test_command_job_wire.py`` for the two-check pattern (serialization guard + wire equivalence).
"""
import pytest

from _builders_asset import CODE_BUILDERS, DATA_BUILDERS, ENVIRONMENT_BUILDERS, MODEL_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes

_ALL = {}
_ALL.update(MODEL_BUILDERS)
_ALL.update(ENVIRONMENT_BUILDERS)
_ALL.update(DATA_BUILDERS)
_ALL.update(CODE_BUILDERS)


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_asset_serializes(case_name):
    """The asset rest object must serialize to wire without raising."""
    entity = _ALL[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_asset_wire_matches_expected(case_name):
    """The asset wire must be byte-identical to the baseline captured from main."""
    entity = _ALL[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
