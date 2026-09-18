# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for feature-store + data-import entities."""
import pytest

from _builders_featurestore import (
    DATA_IMPORT_BUILDERS,
    FEATURE_SET_BUILDERS,
    FEATURE_STORE_ENTITY_BUILDERS,
)
from _wire import assert_wire_matches_expected, assert_serializes

_ALL = {}
_ALL.update(FEATURE_SET_BUILDERS)
_ALL.update(FEATURE_STORE_ENTITY_BUILDERS)
_ALL.update(DATA_IMPORT_BUILDERS)


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_featurestore_serializes(case_name):
    """The feature-store/data-import rest object must serialize to wire without raising."""
    entity = _ALL[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_featurestore_wire_matches_expected(case_name):
    """The feature-store/data-import wire must be byte-identical to the baseline from main."""
    entity = _ALL[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
