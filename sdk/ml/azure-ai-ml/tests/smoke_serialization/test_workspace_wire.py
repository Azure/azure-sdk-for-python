# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wire-serialization smoke tests for workspace / registry entities."""
import pytest

from _builders_workspace import REGISTRY_BUILDERS, WORKSPACE_BUILDERS
from _wire import assert_wire_matches_expected, assert_serializes

_ALL = {}
_ALL.update(WORKSPACE_BUILDERS)
_ALL.update(REGISTRY_BUILDERS)


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_workspace_serializes(case_name):
    """The workspace/registry/connection rest object must serialize to wire without raising."""
    entity = _ALL[case_name]()
    assert_serializes(entity._to_rest_object())


@pytest.mark.parametrize("case_name", sorted(_ALL))
def test_workspace_wire_matches_expected(case_name):
    """The workspace/registry/connection wire must be byte-identical to the baseline from main."""
    entity = _ALL[case_name]()
    assert_wire_matches_expected(case_name, entity._to_rest_object())
